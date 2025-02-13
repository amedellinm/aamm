import argparse

from aamm import file_system as fs
from aamm import testing
from aamm.iterable import group_by, split_iter
from aamm.testing.core import TEST_PREFIX


def main(root: str):
    root = fs.absolute(root)
    all_tests = testing.main(root)

    def printf(line: str) -> str:
        if line.endswith(":"):
            print(1 * "    " + line)
        elif line.startswith(TEST_PREFIX):
            print(2 * "    " + line)
        elif "--" in line:
            print(3 * "    " + line)

    total_count = len(all_tests)
    favorable_count = sum(test.error_name is None for test in all_tests)

    global_score = (
        "ALL"
        if total_count == favorable_count
        else f"{favorable_count:,}/{total_count:,}"
    )
    header = f"Ran {global_score} tests successfully"

    print(f"\n{header}\n{len(header) * '-'}\n")

    for path, tests in group_by((t.module_path, t) for t in all_tests).items():
        successful_tests, failed_tests = split_iter(
            tests, lambda test: test.error_name is None
        )

        module = path.removeprefix(root + fs.SEP)
        module = fs.remove_extension(module)
        module = module.replace(fs.SEP, ".")
        score = f"{len(successful_tests):,}|{len(tests):,}"
        filler = 84 - len(module) - len(score)

        print(f"{module}  {filler*'.'}  {score}")

        for suite, tests in group_by((t.suite_name, t) for t in failed_tests).items():
            printf(f"{suite}:")

            for t in tests:
                printf(f"{t.test_name}")
                printf(f"error -- {t.error_name}: {t.error_message}")
                printf(f"where -- {fs.relative(t.module_path)} {t.where}")

    print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=fs.up(fs.current_directory()))
    main(ap.parse_args().root)
