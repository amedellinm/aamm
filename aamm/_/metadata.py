import ast
import tomllib
from dataclasses import dataclass
from inspect import getdoc
from types import EllipsisType, MemberDescriptorType, ModuleType
from typing import Any

from aamm import file_system as fs
from aamm import meta, metadata
from aamm.graph import depth_first
from aamm.testing.core import test_file

# The folder in which the library lives.
home = fs.up(__file__, 3)

# Read package metadata from "pyproject.toml".
with open(fs.join(home, "pyproject.toml"), "rb") as stream:
    project_data = tomllib.load(stream)["project"]
    name = project_data["name"]
    version = project_data["version"]

# The top level folder of the library.
root = fs.join(home, name)

# A tuple with all the source files in the library.
source_files: tuple[str] = tuple(
    fs.glob(f"{name}{fs.SEP}_/**/*.py", home, with_root=True)
)

# To compute the header files several conditions have to be in place. The following
# snippet retrieves all ".py" files that are not inside the "_", "scripts", or any of
# the "__tests" directories by ignoring any directory name not starting with a letter
# (case insensitive).
condition = lambda x: fs.name(x) != "scripts" and fs.name(x)[0].isalpha()
expand = lambda x: fs.directories(x) if condition(x) else []
header_files = []

for directory in depth_first(root, expand):
    if not condition(directory):
        continue

    for file in fs.files(directory):
        if fs.extension(file) == "py" and fs.name(file) != "metadata":
            header_files.append(file)

# A tuple with all the header files in the library.
header_files: tuple[str] = tuple(header_files)

# A tuple with all the test files in the library.
test_files: tuple[str] = tuple(map(test_file, header_files))


@dataclass(slots=True, eq=False)
class SymbolInfo:
    name: str
    value: Any
    has_docstring: bool
    header_file: str
    is_child: bool
    source_file: str


def api_symbols() -> dict[int, SymbolInfo]:
    """Return a table of symbol:symbol_info for all symbols inside header files."""

    # This is the inverse function of `meta.module_identifier`.
    def path_from_module(module_identifier: str) -> str | EllipsisType:
        base_path = module_identifier.replace(".", fs.SEP)
        module_path = base_path + ".py"
        package_path = fs.join(base_path, "__init__.py")
        return (
            module_path
            if fs.exists(module_path)
            else package_path if fs.exists(package_path) else ...
        )

    # Set up the return data structure.
    symbols: dict[int, SymbolInfo] = {}

    for header_file in metadata.header_files:
        module = meta.import_path(header_file)

        # Similar to `symbols` but uses name instead of id for the key and it is scoped
        # to the current `header_file`. The table is used for the AST exploration.
        file_symbols: dict[str, SymbolInfo] = {}

        for key, val in vars(module).items():
            # Continue if the name doesn't start with a letter.
            if not key[:1].isalpha():
                continue
            if isinstance(val, ModuleType):
                raise RuntimeError(
                    f"module '{key}' exposed in header file '{header_file}'"
                )

            # Gather the information for the fields in `SymbolInfo`.
            src_module = getattr(val, "__module__", None)
            source_file = src_module and path_from_module(src_module)
            has_docstring = ... if not callable(val) else getdoc(val) is not None
            val_id = id(val)

            symbol_info = file_symbols[key] = symbols.setdefault(
                val_id,
                SymbolInfo(key, val, has_docstring, header_file, False, source_file),
            )

            # If the symbol is a class (not a metaclass) and its definition lies within
            # this library, its child symbols are considered as well.
            if (
                not symbol_info.source_file is ...
                and isinstance(val, type)
                and not issubclass(val, type)
            ):

                # Repeat the process above for the children of the class.
                for key, val, base in meta.public_members(val):
                    if isinstance(val, MemberDescriptorType):
                        continue

                    source_file = base.__module__ and path_from_module(base.__module__)
                    has_docstring = (
                        ... if not callable(val) else getdoc(val) is not None
                    )

                    val_id = id(val)
                    symbol_info = file_symbols[key] = symbols.setdefault(
                        val_id,
                        SymbolInfo(
                            key, val, has_docstring, header_file, True, source_file
                        ),
                    )

        # Unlike functions and classes, variables do not contain as much metadata. For
        # them, to compute fields such as the source file, it is necessary to read the
        # files and follow the imports using the `ast` module.
        queue = [header_file]
        known = set()

        while queue:
            try:
                with open(queue.pop()) as file:
                    src = file.read()
            except:
                continue

            # The expression `next(ast.walk(ast.parse(src))).body` grabs the
            # `ast.Module` node of the tree, essentially considering only the symbols at
            # the top level of the file.
            for node in next(ast.walk(ast.parse(src))).body:
                # Header files do not allow ast.Import statements, so ast.ImportFrom is
                # the only one to be taken care of.
                if not isinstance(node, ast.ImportFrom):
                    continue

                source_file = path_from_module(node.module)
                # `source_file` is `...` when the module is external to the library.
                if not (source_file is ... or source_file in known):
                    # Add imported file to the queue to follow the chain.
                    known.add(source_file)
                    queue.append(source_file)

                for symbol in node.names:
                    # account for aliasing
                    name = symbol.asname or symbol.name
                    # Make sure the name is present in the header file.
                    if name not in file_symbols:
                        continue

                    # Update tje `source_file` field.
                    symbols[id(file_symbols[name].value)].source_file = source_file

    return symbols
