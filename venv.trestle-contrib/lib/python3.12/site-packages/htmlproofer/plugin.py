import concurrent.futures
import fnmatch
from functools import lru_cache, partial
import os.path
import pathlib
import re
import threading
import time
from typing import Dict, List, Optional, Set
import urllib.parse
import uuid

from bs4 import BeautifulSoup, SoupStrainer
from markdown.extensions.toc import slugify
from mkdocs import utils
from mkdocs.config import Config, config_options
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page
import requests
import urllib3

URL_TIMEOUT = 10.0
_URL_BOT_ID = f'Bot {uuid.uuid4()}'
URL_HEADERS = {'User-Agent': _URL_BOT_ID, 'Accept-Language': '*'}
NAME = "htmlproofer"

MARKDOWN_ANCHOR_PATTERN = re.compile(r'([^#]+)(#(.+))?')
HEADING_PATTERN = re.compile(r'\s*#+\s*(.*)')
HTML_LINK_PATTERN = re.compile(r'<a (?:id|name)=\"([^\"]+)\">')
IMAGE_PATTERN = re.compile(r'\[\!\[.*\]\(.*\)\].*|\!\[.*\]\[.*\].*')
LOCAL_PATTERNS = [
    re.compile(rf'https?://{local}')
    for local in ('localhost', '127.0.0.1', 'app_server')
]
ATTRLIST_ANCHOR_PATTERN = re.compile(r'\{.*?\#([^\s\}]*).*?\}')
ATTRLIST_PATTERN = re.compile(r'\{.*?\}')

# Example emojis:
#   :banana:
#   :smiley_cat:
#   :octicons-apps-16:
#   :material-star:
EMOJI_PATTERN = re.compile(r'\:[a-z0-9_-]+\:')

urllib3.disable_warnings()


def log_info(msg, *args, **kwargs):
    utils.log.info(f"{NAME}: {msg}", *args, **kwargs)


def log_warning(msg, *args, **kwargs):
    utils.log.warning(f"{NAME}: {msg}", *args, **kwargs)


def log_error(msg, *args, **kwargs):
    utils.log.error(f"{NAME}: {msg}", *args, **kwargs)


class HtmlProoferPlugin(BasePlugin):
    files: List[File]
    invalid_links = False

    config_scheme = (
        ("enabled", config_options.Type(bool, default=True)),
        ('raise_error', config_options.Type(bool, default=False)),
        ('raise_error_after_finish', config_options.Type(bool, default=False)),
        ('raise_error_excludes', config_options.Type(dict, default={})),
        ('skip_downloads', config_options.Type(bool, default=False)),
        ('validate_external_urls', config_options.Type(bool, default=True)),
        ('validate_rendered_template', config_options.Type(bool, default=False)),
        ('ignore_urls', config_options.Type(list, default=[])),
        ('warn_on_ignored_urls', config_options.Type(bool, default=False)),
        ('ignore_pages', config_options.Type(list, default=[])),
        ('retry_max_times', config_options.Type(int, default=0)),
        ('max_workers', config_options.Type(int, default=None)),
    )

    def __init__(self):
        self._local = threading.local()
        self.files = []
        self.scheme_handlers = {
            "http": partial(HtmlProoferPlugin.resolve_web_scheme, self),
            "https": partial(HtmlProoferPlugin.resolve_web_scheme, self),
        }
        super().__init__()

    def _get_session(self) -> requests.Session:
        """Return a per-thread `requests.Session`, creating one lazily if needed."""
        session = getattr(self._local, 'session', None)
        if session is None:
            session = requests.Session()
            session.verify = False
            session.headers.update(URL_HEADERS)
            session.max_redirects = 5
            self._local.session = session
        return session

    def on_post_build(self, config: Config) -> None:
        if self.config['raise_error_after_finish'] and self.invalid_links:
            raise PluginError("Invalid links present.")

    def on_files(self, files: Files, config: Config) -> None:
        # Store files to allow inspecting Markdown files in later stages.
        # The values in files at this point are not guaranteed to be the same as the ones in the Page objects.
        # For example, material blog plugin may modify the files after this event.
        for f in files:
            self.files.append(f)

    def on_post_page(self, output_content: str, page: Page, config: Config) -> None:
        if not self.config['enabled']:
            return

        # Optimization: At this point, we have all the files, so we can create
        # a dictionary for faster lookups. Prior to this point, files are
        # still being updated so creating a dictionary before now would result
        # in incorrect values appearing as the key.
        opt_files = {}
        opt_files.update({os.path.normpath(file.url): file for file in self.files})
        opt_files.update({os.path.normpath(file.src_uri): file for file in self.files})

        # Optimization: only parse links and headings
        # li, sup are used for footnotes
        strainer = SoupStrainer(('a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'sup', 'img'))

        content = output_content if self.config['validate_rendered_template'] else page.content
        soup = BeautifulSoup(str(content), 'html.parser', parse_only=strainer)

        all_element_ids = set(str(tag['id']) for tag in soup.select('[id]'))
        all_element_ids.add('')  # Empty anchor is commonly used, but not real

        urls = (set(str(a['href']) for a in soup.find_all('a', href=True)) |
                set(str(img['src']) for img in soup.find_all('img')))

        urls_to_check: List[str] = []
        for url in urls:
            if any(fnmatch.fnmatch(url, ignore_url) for ignore_url in self.config['ignore_urls']):
                if self.config['warn_on_ignored_urls']:
                    log_warning(f"ignoring URL {url} from {page.file.src_path}")
            elif any(
                fnmatch.fnmatch(page.file.src_path, ignore_page)
                for ignore_page in self.config['ignore_pages']
            ):
                if self.config['warn_on_ignored_urls']:
                    log_warning(f"ignoring URL {url} from {page.file.src_path}")
            else:
                urls_to_check.append(url)

        # Note on exception propagation: `future.result()` re-raises any exception
        # from a worker thread. If `raise_error` is `True` and multiple URLs fail
        # concurrently, only the first exception to be observed here will propagate;
        # remaining futures continue to execute but their exceptions are not raised.
        # This is acceptable because each thread independently logs/reports its
        # failure via `report_invalid_url` before raising, so no errors are silently
        # lost. When `raise_error_after_finish` is used instead, all failures are
        # recorded via the `invalid_links` flag and surfaced in `on_post_build`.
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            for future in concurrent.futures.as_completed(
                executor.submit(self.check_url, url, page.file.src_path, all_element_ids, opt_files) for url in urls_to_check
            ):
                future.result()

    def report_invalid_url(self, url, url_status, src_path):
        error = f'invalid url - {url} [{url_status}] [{src_path}]'
        if self.config['raise_error']:
            raise PluginError(error)
        elif self.config['raise_error_after_finish']:
            log_error(error)
            self.invalid_links = True
        else:
            log_warning(error)

    def get_external_url(self, url, scheme, src_path):
        try:
            return self.scheme_handlers[scheme](url)
        except KeyError:
            log_info(f'Unknown url-scheme "{scheme}:" detected. "{url}" from "{src_path}" will not be checked.')
        return 0

    @lru_cache(maxsize=1000)
    def resolve_web_scheme(self, url: str) -> int:
        try:
            response = self._get_session().get(url, timeout=URL_TIMEOUT, stream=True)

            if self.config['skip_downloads'] is False:
                # Download the entire contents as to not break previous behaviour.
                for _ in response.iter_content(chunk_size=1024 * 1024):
                    pass

            return response.status_code
        except requests.exceptions.Timeout:
            return 504
        except requests.exceptions.TooManyRedirects:
            return -1
        except requests.exceptions.ConnectionError:
            return -1

    def check_url(
            self,
            url: str,
            src_path: str,
            all_element_ids: Set[str],
            files: Dict[str, File],
            ) -> None:
        retry_times = 0
        retry_max_times = self.config['retry_max_times']
        retry_duration = 2
        while retry_times <= retry_max_times:
            url_status = self.get_url_status(url, src_path, all_element_ids, files)
            retry_times += 1
            if self.bad_url(url_status) and self.is_error(self.config, url, url_status):
                if retry_times > retry_max_times:
                    self.report_invalid_url(url, url_status, src_path)
                else:
                    log_info(f"Retrying URL {url} from {src_path} after {retry_duration} seconds...")
                    time.sleep(retry_duration)
                    retry_duration *= 2

    def get_url_status(
            self,
            url: str,
            src_path: str,
            all_element_ids: Set[str],
            files: Dict[str, File]
    ) -> int:
        if any(pat.match(url) for pat in LOCAL_PATTERNS):
            return 0

        scheme, _, path, _, fragment = urllib.parse.urlsplit(url)
        if scheme:
            if self.config['validate_external_urls']:
                return self.get_external_url(url, scheme, src_path)
            return 0
        if fragment and not path:
            return 0 if url[1:] in all_element_ids else 404
        else:
            is_valid = self.is_url_target_valid(url, src_path, files)
            url_status = 404
            if not is_valid and self.is_error(self.config, url, url_status):
                log_warning(f"Unable to locate source file for: {url}")
                return url_status
            return 0

    @staticmethod
    def is_url_target_valid(url: str, src_path: str, files: Dict[str, File]) -> bool:
        match = MARKDOWN_ANCHOR_PATTERN.match(url)
        if match is None:
            return True

        url_target, _, optional_anchor = match.groups()
        source_file = HtmlProoferPlugin.find_source_file(url_target, src_path, files)
        if source_file is None:
            return False

        # If there's an anchor (fragment) on the link, we try to find it in the source_file
        if optional_anchor:
            _, extension = os.path.splitext(source_file.src_uri)
            # Currently only Markdown-based pages are supported, but conceptually others could be added below
            if extension == ".md":
                if source_file.page is None or source_file.page.markdown is None:
                    return False
                if not HtmlProoferPlugin.contains_anchor(source_file.page.markdown, optional_anchor):
                    return False

        return True

    @staticmethod
    def find_target_markdown(url: str, src_path: str, files: Dict[str, File]) -> Optional[str]:
        """From a built URL, find the original Markdown source from the project that built it."""

        file = HtmlProoferPlugin.find_source_file(url, src_path, files)
        if file and file.page:
            return file.page.markdown
        return None

    @staticmethod
    def find_source_file(url: str, src_path: str, files: Dict[str, File]) -> Optional[File]:
        """From a built URL, find the original file from the project that built it."""

        if len(url) > 1 and url[0] == '/':
            # Convert root/site paths
            search_path = os.path.normpath(url[1:])
        else:
            # Handle relative links by looking up the destination url for the
            # src_path and getting the parent directory.
            try:
                dest_uri = files[src_path].dest_uri
                src_dir = urllib.parse.quote(str(pathlib.Path(dest_uri).parent), safe='/\\')
                search_path = os.path.normpath(str(pathlib.Path(src_dir) / pathlib.Path(url)))
            except KeyError:
                return None

        try:
            return files[search_path]
        except KeyError:
            return None

    @staticmethod
    def contains_anchor(markdown: str, anchor: str) -> bool:
        """Check if a set of Markdown source text contains a heading that corresponds to a
        given anchor."""
        for line in markdown.splitlines():
            # Markdown allows whitespace before headers and an arbitrary number of #'s.
            heading_match = HEADING_PATTERN.match(line)
            if heading_match is not None:
                heading = heading_match.groups()[0]

                # Headings are allowed to have attr_list after them, of the form:
                # # Heading { #testanchor .testclass }
                # # Heading {: #testanchor .testclass }
                # # Heading {.testclass #testanchor}
                # # Heading {.testclass}
                # these can override the headings anchor id, or alternatively just provide additional class etc.
                attr_list_anchor_match = ATTRLIST_ANCHOR_PATTERN.match(heading)
                if attr_list_anchor_match is not None:
                    attr_list_anchor = heading_match.groups()[1]
                    if anchor == attr_list_anchor:
                        return True

                heading = re.sub(ATTRLIST_PATTERN, '', heading)  # remove any attribute list from heading, before slugify

                # Headings are allowed to have images after them, of the form:
                # # Heading [![Image](image-link)] or ![Image][image-reference]
                # But these images are not included in the generated anchor, so remove them.
                heading = re.sub(IMAGE_PATTERN, '', heading)

                # Headings are allowed to have emojis in them under certain Mkdocs themes.
                # https://squidfunk.github.io/mkdocs-material/setup/extensions/python-markdown-extensions/#emoji
                heading = re.sub(EMOJI_PATTERN, '', heading)

                anchor_slug = slugify(heading, '-')
                if anchor == anchor_slug:
                    return True

            # Check for HTML anchors using id or name attributes
            # Multiple anchors can exist on a single line, so find all of them
            for html_anchor in re.findall(HTML_LINK_PATTERN, line):
                if anchor == html_anchor:
                    return True

            # Any attribute list at end of paragraphs or after images can also generate an anchor (in addition to
            # the heading ones) so gather those and check as well (multiple could be a line so gather all)
            for attr_list_anchor in re.findall(ATTRLIST_ANCHOR_PATTERN, line):
                if anchor == attr_list_anchor:
                    return True

        return False

    @staticmethod
    def bad_url(url_status: int) -> bool:
        if url_status == -1:
            return True
        elif url_status >= 400:
            return True
        else:
            return False

    @staticmethod
    def is_error(config: Config, url: str, url_status: int) -> bool:
        excludes = config['raise_error_excludes'].get(url_status, [])

        if any(fnmatch.fnmatch(url, exclude_url) for exclude_url in excludes):
            return False
        else:
            return True
