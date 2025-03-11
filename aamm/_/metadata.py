import tomllib

from aamm import file_system as fs
from aamm.graph import depth_first
from aamm.testing.core import is_test_file

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


header_files = []


def condition(directory: str) -> bool:
    return fs.name(directory) != "scripts" and fs.name(directory)[0].isalpha()


def expand(directory: str) -> list[str]:
    return fs.directories(directory) if condition(directory) else []


for directory in depth_first(root, expand):
    if not condition(directory):
        continue

    for file in fs.files(directory):
        if fs.extension(file) == "py":
            header_files.append(file)

header_files: tuple[str] = tuple(header_files)

fs.cd(cwd)
