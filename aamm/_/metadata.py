import ast
import importlib
import inspect
import tomllib
from dataclasses import dataclass
from types import EllipsisType
from typing import Any

from aamm import file_system as fs
from aamm import meta, metadata
from aamm.graph import depth_first

# The directory in which the library lives.
home = fs.up(__file__, 3)

# Read package metadata from "pyproject.toml".
with open(fs.join(home, "pyproject.toml"), "rb") as stream:
    project_data = tomllib.load(stream)["project"]
    name = project_data["name"]
    version = project_data["version"]

# The top level directory of the library.
root = fs.join(home, name)

# A tuple with all the source files in the library.
source_files: tuple[str] = tuple(
    fs.glob(f"{name}{fs.SEP}_/**/*.py", home, with_root=True)
)

# To compute the header files several conditions have to be in place. The following
# snippet retrieves all ".py" files that are not inside the "_", "scripts", or any of
# the "__tests" directories.
condition = lambda x: fs.name(x) != "scripts" and fs.name(x)[0].isalpha()
expand = lambda x: fs.directories(x) if condition(x) else []
header_files = []

for directory in depth_first(root, expand):
    if not condition(directory):
        continue

    for file in fs.files(directory):
        if fs.has_extension(file, "py"):
            header_files.append(file)

# A tuple with all the header files in the library.
header_files.remove(fs.join(root, "metadata.py"))
header_files: tuple[str] = tuple(header_files)


def test_file(header_file: str) -> str:
    """Return the test file corresponding to `header_file`."""
    leaf = (
        fs.name(fs.directory(header_file)) + ".py"
        if fs.leaf(header_file) == "__init__.py"
        else fs.leaf(header_file)
    )
    return fs.with_leaf(header_file, f"__tests{fs.SEP}" + leaf)


# A tuple with all the test files in the library.
test_files: tuple[str] = tuple(map(test_file, header_files))

# Check there are not two header files with the same test file.
# This can happen when there is a pair of files such as:
#   .../bla/bla.py
#   .../bla/__init__.py
# Which should be avoided.
assert len(test_files) == len(frozenset(test_files))


@dataclass(slots=True, eq=False)
class SymbolInfo:
    name: str
    value: Any
    header_file: str
    module_name: str
    is_class_member: bool = False
    has_docstring: bool | EllipsisType = ...
    source_file: str | None = None


class FromImportSymbol:
    def __eq__(self, other: "FromImportSymbol") -> bool:
        return isinstance(other, type(self)) and self.alias == other.alias

    def __hash__(self) -> int:
        return hash(self.alias)

    def __init__(self, name: str, alias: str | None, module_name: str):
        self.name = name
        self.alias = alias
        self.module_name = module_name

    def __lt__(self, other: "FromImportSymbol") -> bool:
        return (self.module_name, self.alias) < (other.module_name, other.alias)


def from_import_symbols(path: str) -> frozenset[FromImportSymbol]:
    with open(path) as file:
        src = file.read()
    return frozenset(
        {
            FromImportSymbol(symbol.name, symbol.asname or symbol.name, node.module)
            for node in reversed(next(ast.walk(ast.parse(src))).body)
            if isinstance(node, ast.ImportFrom)
            for symbol in node.names
        }
    )


def is_local_module(module_name: str) -> str | None:
    base = module_name.replace(".", fs.SEP)

    package_path = fs.join(metadata.home, base, "__init__.py")
    if fs.exists(package_path):
        return package_path

    module_path = fs.join(metadata.home, base + ".py")
    if fs.exists(module_path):
        return module_path


def source_file(symbol: FromImportSymbol) -> str | None:
    if module_path := is_local_module(symbol.module_name):
        for s in from_import_symbols(module_path):
            if symbol.name == s.alias:
                return source_file(s)

    return module_path or None


def has_docstring(symbol: Any) -> bool | EllipsisType:
    return bool(inspect.getdoc(symbol)) if callable(symbol) else ...


ignored_members = {
    "__abstractmethods__",
    "__annotations__",
    "__dataclass_fields__",
    "__dataclass_params__",
    "__dict__",
    "__doc__",
    "__init__",
    "__match_args__",
    "__module__",
    "__repr__",
    "__slots__",
    "__weakref__",
}


def api_symbols():
    """Return a table of symbol:symbol_info for all symbols inside header files."""

    symbols: dict[int, SymbolInfo] = {}

    for header_file in metadata.header_files:
        module_name = meta.module_name(fs.relative(header_file, metadata.home))
        module = importlib.import_module(module_name)

        for symbol in from_import_symbols(header_file):
            value = getattr(module, symbol.alias)

            symbols[id(value)] = SymbolInfo(
                symbol.alias,
                value,
                header_file,
                module_name,
                False,
                has_docstring(value),
                source_file(symbol),
            )

            if not isinstance(value, type):
                continue

            for name, member, Type in meta.members(value):
                if name in ignored_members:
                    continue

                alias = f"{Type.__qualname__}.{name}"
                if inspect.ismethod(member):
                    member = member.__func__
                    alias += ".__func__"

                symbols[id(member)] = SymbolInfo(
                    alias,
                    member,
                    header_file,
                    module_name,
                    True,
                    has_docstring(member),
                    is_local_module(Type.__module__),
                )

    return symbols
