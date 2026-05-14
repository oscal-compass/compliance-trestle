import distutils.ccompiler
import distutils.dist
import glob
import os

import cffi


# Get the directory for the cmark source files. It's under the package root
# as /third_party/cmark/src
HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.abspath(os.path.join(HERE, '../../'))
SRC_DIR = os.path.join(PACKAGE_ROOT, 'third_party/cmark/src')
EXTENSIONS_SRC_DIR = os.path.join(PACKAGE_ROOT, 'third_party/cmark/extensions')
UNIX_GENERATED_SRC_DIR = os.path.join(PACKAGE_ROOT, 'generated', 'unix')
WIN_GENERATED_SRC_DIR = os.path.join(PACKAGE_ROOT, 'generated', 'windows')

CMARK_DEF_H_PATH = os.path.join(HERE, 'cmark.cffi.h')
CMARK_MODULE_H_PATH = os.path.join(HERE, 'cmark_module.h')

with open(CMARK_DEF_H_PATH, encoding='utf-8') as fh:
    CMARK_DEF_H = fh.read()

with open(CMARK_MODULE_H_PATH, encoding='utf-8') as fh:
    CMARK_MODULE_H = fh.read()


def _get_sources(dir, exclude=set()):
    sources = glob.iglob(os.path.join(dir, '*.c'))
    return sorted([
        os.path.relpath(path, start=PACKAGE_ROOT)
        for path in
        sources
        if os.path.basename(path) not in exclude
    ])


SOURCES = _get_sources(SRC_DIR, exclude={'main.c'})
SOURCES.extend(_get_sources(EXTENSIONS_SRC_DIR))


def _compiler_type():
    """
    Gets the compiler type from distutils. On Windows with MSVC it will be
    "msvc". On macOS and linux it is "unix".

    Borrowed from https://github.com/pyca/cryptography/blob\
        /05b34433fccdc2fec0bb014c3668068169d769fd/src/_cffi_src/utils.py#L78
    """
    dist = distutils.dist.Distribution()
    dist.parse_config_files()
    cmd = dist.get_command_obj('build')
    cmd.ensure_finalized()
    compiler = distutils.ccompiler.new_compiler(compiler=cmd.compiler)
    return compiler.compiler_type


COMPILER_TYPE = _compiler_type()
# Note: on Windows with MSVC the compiler type is 'msvc'. On macOS and
# Linux it is 'unix'. For MinGW on Windows distutils reports 'mingw32'.
# Select the appropriate compile args and generated sources directory
# based solely on the compiler type.
if COMPILER_TYPE in {'unix', 'mingw32'}:
    EXTRA_COMPILE_ARGS = ['-std=c99']
    GENERATED_SRC_DIR = UNIX_GENERATED_SRC_DIR
elif COMPILER_TYPE == 'msvc':
    EXTRA_COMPILE_ARGS = ['/TP']
    GENERATED_SRC_DIR = WIN_GENERATED_SRC_DIR
else:
    raise AssertionError("unsupported compiler: %s" % COMPILER_TYPE)


ffibuilder = cffi.FFI()
ffibuilder.cdef(CMARK_DEF_H)
ffibuilder.set_source(
    'cmarkgfm._cmark',
    CMARK_MODULE_H,
    sources=SOURCES,
    include_dirs=[SRC_DIR, EXTENSIONS_SRC_DIR, GENERATED_SRC_DIR],
    extra_compile_args=EXTRA_COMPILE_ARGS
)


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
