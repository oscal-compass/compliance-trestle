"""
An MkDocs plugin to minify HTML, JS or CSS files prior to being written to disk
"""
import hashlib
from pathlib import Path
import os
from typing import Callable, Dict, List, Optional, Tuple, Union

import csscompressor
import htmlmin
import jsmin
import mkdocs.config.config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page
from packaging import version

EXTRAS: Dict[str, str] = {
    "js": "extra_javascript",
    "css": "extra_css",
}

MINIFIERS: Dict[str, Callable] = {
    "js": jsmin.jsmin,
    "css": csscompressor.compress,
}

if version.parse(csscompressor.__version__) <= version.parse("0.9.5"):
    # Monkey patch csscompressor 0.9.5
    # See https://github.com/sprymix/csscompressor/issues/9#issuecomment-1024417374
    _preserve_call_tokens_original = csscompressor._preserve_call_tokens
    _url_re = csscompressor._url_re

    def my_new_preserve_call_tokens(*args, **kwargs):
        """If regex is for url pattern, switch the keyword remove_ws to False
        Such configuration will preserve svg code in url() pattern of CSS file.
        """
        if _url_re == args[1]:
            kwargs["remove_ws"] = False
        return _preserve_call_tokens_original(*args, **kwargs)

    csscompressor._preserve_call_tokens = my_new_preserve_call_tokens

    assert csscompressor._preserve_call_tokens == my_new_preserve_call_tokens


class MinifyPlugin(BasePlugin):
    """Custom minify plugin class"""

    config_scheme: Tuple = (
        ("minify_html", mkdocs.config.config_options.Type(bool, default=False)),
        ("minify_js", mkdocs.config.config_options.Type(bool, default=False)),
        ("minify_css", mkdocs.config.config_options.Type(bool, default=False)),
        ("js_files", mkdocs.config.config_options.Type((str, list), default=None)),
        ("css_files", mkdocs.config.config_options.Type((str, list), default=None)),
        ("htmlmin_opts", mkdocs.config.config_options.Type((str, dict), default=None)),
        ("cache_safe", mkdocs.config.config_options.Type(bool, default=False)),
    )

    path_to_hash: Dict[str, str] = {}
    """
    The file hash is stored in a dict, so that it's generated only once.
    Relevant only when `on_pre_build` is run AND `cache_safe` is `True`.
    """

    path_to_data: Dict[str, str] = {}
    """
    The file data is stored in a dict, so that it's read only once.
    Relevant only when `on_pre_build` is run AND `cache_safe` is `True`.
    """

    def _minified_asset(self, file_name: str, file_type: str, file_hash: str) -> str:
        """Add [.hash].min. text to the asset file name."""
        hash_part: str = f".{file_hash[:6]}" if file_hash else ""
        min_part: str = ".min" if self.config[f"minify_{file_type}"] else ""
        return file_name.replace(f".{file_type}", f"{hash_part}{min_part}.{file_type}")

    def _minify(self, file_type: str, config: MkDocsConfig) -> None:
        """Process extras and save them to disk."""
        minify_func: Callable = MINIFIERS[file_type]
        file_paths: Union[str, List[str]] = self.config[f"{file_type}_files"] or []

        if not isinstance(file_paths, list):
            file_paths = [file_paths]

        site_dir = Path(config['site_dir'])

        file_paths2 = []
        for file_path in file_paths.copy():
            if "*" in file_path:
                glob_parts = file_path.split("*", maxsplit=1)
                glob_dir = site_dir / Path(glob_parts[0])
                file_path = glob_dir.glob(f"*{glob_parts[1]}")

                for glob_file in file_path:
                    file_paths2.append(glob_file)
            else:
                file_paths2.append(site_dir / file_path)

        # remove duplicates
        file_paths2 = list(set(file_paths2))

        for file_path in file_paths2:
            site_file_path: str = str(file_path.as_posix())
            rel_file_path: str = site_file_path.replace(site_dir.as_posix(), "").strip("/")

            with open(site_file_path, mode="r+", encoding="utf8") as file:
                if self.config["cache_safe"]:
                    file.write(self.path_to_data[rel_file_path])
                else:
                    minified: str = self._minify_file_data_with_func(file.read(), minify_func)
                    file.seek(0)
                    file.write(minified)
                file.truncate()

            file_hash: str = self.path_to_hash.get(rel_file_path, "")

            # Rename to [.hash].min.{file_type}
            os.rename(site_file_path, self._minified_asset(site_file_path, file_type, file_hash))

    @staticmethod
    def _minify_file_data_with_func(file_data: str, minify_func: Callable) -> str:
        """Use the minify_func and return the minified data"""
        if minify_func.__name__ == "jsmin":
            return minify_func(file_data, quote_chars="'\"`")
        else:
            return minify_func(file_data)

    def _minify_html_page(self, output: str) -> Optional[str]:
        """Minify HTML page content."""
        if not self.config["minify_html"]:
            return output

        output_opts: Dict[str, Union[bool, str, Tuple[str, ...]]] = {
            "remove_comments": False,
            "remove_empty_space": False,
            "remove_all_empty_space": False,
            "reduce_empty_attributes": True,
            "reduce_boolean_attributes": False,
            "remove_optional_attribute_quotes": True,
            "convert_charrefs": True,
            "keep_pre": False,
            "pre_tags": ("pre", "textarea"),
            "pre_attr": "pre",
        }

        selected_opts: Dict = self.config["htmlmin_opts"] or {}

        for key in selected_opts:
            if key in output_opts:
                output_opts[key] = selected_opts[key]
            else:
                print(f"htmlmin option '{key}' not recognized")

        return htmlmin.minify(output, **output_opts)

    def _minify_extra_config(self, file_type: str, config: MkDocsConfig) -> None:
        """Change extra_ entries, so they point to the minified/hashed file names."""
        files_to_minify: Union[str, List[str]] = self.config[f"{file_type}_files"] or []
        minify_func: Callable = MINIFIERS[file_type]
        minify_flag: bool = self.config[f"minify_{file_type}"]
        extra: str = EXTRAS[file_type]

        if not isinstance(files_to_minify, list):
            files_to_minify = [files_to_minify]

        for i, extra_item in enumerate(config[extra]):
            file_path = str(extra_item)

            if file_path not in files_to_minify:
                continue

            file_hash: str = ""

            # When `cache_safe`, the hash is needed before the build,
            # so it's generated from the data from the source file.
            # A valid path in a custom_dir takes priority.
            if self.config["cache_safe"]:
                docs_file_path: str = f"{config['docs_dir']}/{file_path}".replace("\\", "/")
                theme = config.theme

                # Since MkDocs 1.5.0, theme.custom_dir is available for direct access
                if not hasattr(theme, "custom_dir"):
                    for user_config in config.user_configs:
                        user_config: Dict
                        custom_dir: str = user_config.get("theme", {}).get("custom_dir", "")
                        temp_path: str = f"{custom_dir}/{file_path}".replace("\\", "/")
                        if custom_dir and os.path.exists(temp_path):
                            docs_file_path = temp_path
                            break
                elif theme.custom_dir:
                    temp_path: str = f"{theme.custom_dir}/{file_path}".replace("\\", "/")
                    if os.path.exists(temp_path):
                        docs_file_path = temp_path

                with open(docs_file_path, encoding="utf8") as file:
                    file_data: str = file.read()

                    if minify_flag:
                        file_data = self._minify_file_data_with_func(file_data, minify_func)

                    # store data for use in `on_post_build`
                    self.path_to_data[file_path] = file_data

                file_hash = hashlib.sha384(file_data.encode("utf8")).hexdigest()
                # store hash for use in `on_post_build`
                self.path_to_hash[file_path] = file_hash

            new_file_path = self._minified_asset(file_path, file_type, file_hash)
            if isinstance(extra_item, str):
                config[extra][i] = new_file_path
            else:  # MkDocs 1.5: ExtraScriptValue.path
                extra_item.path = new_file_path

    def on_post_page(self, output: str, *, page: Page, config: MkDocsConfig) -> Optional[str]:
        """Minify HTML page before saving to disk."""
        return self._minify_html_page(output)

    def on_post_template(
        self, output_content: str, *, template_name: str, config: MkDocsConfig
    ) -> Optional[str]:
        """Minify HTML template files, e.g. 404.html, before saving to disk."""
        if template_name.endswith(".html"):
            return self._minify_html_page(output_content)

        return output_content

    def on_pre_build(self, *, config: MkDocsConfig) -> None:
        """Process file names of extras in the config."""
        if self.config["minify_js"] or self.config["cache_safe"]:
            self._minify_extra_config("js", config)
        if self.config["minify_css"] or self.config["cache_safe"]:
            self._minify_extra_config("css", config)

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        """Process extras before saving to disk."""
        if self.config["minify_js"] or self.config["cache_safe"]:
            self._minify("js", config)
        if self.config["minify_css"] or self.config["cache_safe"]:
            self._minify("css", config)
