import ast
import tomllib
from dataclasses import dataclass
from inspect import getdoc
from types import EllipsisType
from typing import Any

from aamm import file_system as fs
from aamm import meta, metadata
from aamm.graph import depth_first
from aamm.testing.core import is_test_file


def path_from_module(module_identifier: str) -> str | EllipsisType:
    base_path = module_identifier.replace(".", fs.SEP)
    module_path = base_path + ".py"
    package_path = fs.join(base_path, "__init__.py")
    ans = (
        module_path
        if fs.exists(module_path)
        else package_path if fs.exists(package_path) else ...
    )
    return ans


@dataclass(slots=True)
class SymbolInfo:
    has_docstring: bool
    header_files: set[str]
    is_child: bool
    source_file: str

    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and self.source_file == other.source_file

    def __hash__(self) -> int:
        return hash(self.source_file)

    def __lt__(self, other) -> bool:
        return self.self.source_file < other.self.source_file


@dataclass(slots=True)
class Symbol:
    name: str
    value: Any

    def __eq__(self, other) -> bool:
        return id(self.value) == id(other.value)

    def __hash__(self) -> int:
        return id(self.value)

    def __lt__(self, other) -> bool:
        return (self.header_file, self.name) < (other.header_file, other.name)

    def __str__(self) -> str:
        return f"{self.name}@{self.header_file}"


def api_symbols():
    cwd = fs.cwd()
    fs.cd(home)

    symbols: dict[Symbol, SymbolInfo] = {}

    for header_file in map(fs.relative, metadata.header_files):
        module = meta.import_path(header_file)

        file_symbols: dict[str, Symbol] = {}

        for key, val in vars(module).items():

            if not key[:1].isalpha():
                continue

            src_module = getattr(val, "__module__", None)
            source_file = src_module and path_from_module(src_module)
            has_docstring = ... if not callable(val) else getdoc(val) is not None

            symbol = file_symbols[key] = Symbol(key, val)
            symbol_info = symbols.setdefault(
                symbol, SymbolInfo(has_docstring, set(), False, source_file)
            )
            symbol_info.header_files.add(header_file)

            if (
                not symbol_info.source_file is ...
                and isinstance(val, type)
                and not issubclass(val, type)
            ):
                for key, val, base in meta.public_members(val):
                    source_file = base.__module__ and path_from_module(base.__module__)
                    has_docstring = (
                        ... if not callable(val) else getdoc(val) is not None
                    )

                    symbol = file_symbols[key] = Symbol(key, val)
                    symbol_info = symbols.setdefault(
                        symbol, SymbolInfo(has_docstring, set(), True, source_file)
                    )
                    symbol_info.header_files.add(header_file)

        queue = [header_file]
        while queue:
            with open(queue.pop()) as file:
                src = file.read()

            for node in next(ast.walk(ast.parse(src))).body:
                if not isinstance(node, ast.ImportFrom):
                    continue

                source_file = path_from_module(node.module)
                if source_file is not ...:
                    queue.append(source_file)

                for symbol in node.names:
                    name = symbol.asname or symbol.name
                    if name not in file_symbols:
                        continue
                    symbols[file_symbols[name]].source_file = source_file

    fs.cd(cwd)

    return symbols


home = fs.up(fs.current_file(), 3)

cwd = fs.cwd()
fs.cd(home)

with open("pyproject.toml", "rb") as stream:
    data = tomllib.load(stream)
    name = data["project"]["name"]
    version = data["project"]["version"]

root = fs.join(home, name)

test_files: tuple[str] = tuple(
    fs.resolve(path) for path in fs.glob(f"{name}/**/*.py", home) if is_test_file(path)
)

source_files: tuple[str] = tuple(map(fs.resolve, fs.glob(f"{name}{fs.SEP}_/**/*.py")))


def condition(directory: str) -> bool:
    return fs.name(directory) != "scripts" and fs.name(directory)[0].isalpha()


def expand(directory: str) -> list[str]:
    return fs.directories(directory) if condition(directory) else []


header_files = []

for directory in depth_first(root, expand):
    if not condition(directory):
        continue

    for file in fs.files(directory):
        if fs.extension(file) == "py":
            header_files.append(file)

header_files: tuple[str] = tuple(header_files)


fs.cd(cwd)
