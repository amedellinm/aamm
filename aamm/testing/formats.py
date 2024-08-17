from aamm.strings import TAB


def module_line(
    module_name: str,
    successful_tests: int,
    total_tests: int,
    total_duration: float,
) -> str:
    return (
        TAB
        + f"{module_name} ".ljust(50, ".")
        + f" {successful_tests}/{total_tests}"
        + f" successful tests in {total_duration:.2f} ms\n"
    )


def failed_test(
    test_name: str,
    exception_name: str,
    line_number,
    exception_message: str,
    source_code: str,
) -> str:
    return (
        f"{test_name} -> {exception_name} (line {line_number})\n"
        f"{TAB}err :: {exception_message}\n"
        f"{TAB}src :: {source_code}"
    )
