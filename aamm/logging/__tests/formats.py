from aamm import testing
from aamm.logging import formats as fmts
from aamm.testing import asserts


class TestLogger(testing.TestSuite):
    @testing.subjects(fmts.attribute_error)
    def test_attribute_error(self):
        expected = "'str' object has no attribute 'cat'"
        obtained = fmts.attribute_error("a", "cat")
        asserts.equal(expected, obtained)

    @testing.subjects(fmts.contents_table_row)
    def test_contents_table_row(self):
        expected = "1 ................ 2"
        obtained = fmts.contents_table_row(1, 2, 20)
        asserts.equal(expected, obtained)

    @testing.subjects(fmts.exception_message)
    def test_exception_message(self):
        expected = "Exception: error message"
        obtained = fmts.exception_message(Exception("error message"))
        asserts.equal(expected, obtained)

    @testing.subjects(fmts.function_call)
    def test_function_call(self):
        expected = "print('Hello', world='World')"
        obtained = fmts.function_call("print", "Hello", world="World")
        asserts.equal(expected, obtained)

    @testing.subjects(fmts.index_error)
    def test_index_error(self):
        expected = "index 0 out of range for 'list' object of length 0"
        obtained = fmts.index_error([], 0)
        asserts.equal(expected, obtained)

    @testing.subjects(fmts.key_error)
    def test_key_error(self):
        expected = "'key' not in 'dict' object"
        obtained = fmts.key_error({}, "key")
        asserts.equal(expected, obtained)

    @testing.subjects(fmts.operand_error)
    def test_operand_error(self):
        expected = "invalid operator '+' for operand(s): 2, '2'"
        obtained = fmts.operand_error("+", 2, "2")
        asserts.equal(expected, obtained)

    @testing.subjects(fmts.qualname)
    def test_qualname(self):
        expected = "str"
        obtained = fmts.qualname("")
        asserts.equal(expected, obtained)

    @testing.subjects(fmts.table)
    def test_table(self):
        expected = "a  1  \nb  10 \nc  100"
        obtained = fmts.table("abc", ["1", "10", "100"])
        asserts.equal(expected, obtained)

    @testing.subjects(fmts.traceback)
    def test_traceback(self):
        pass

    @testing.subjects(fmts.type_error)
    def test_type_error(self):
        expected = "expected type(s) int | str, got NoneType"
        obtained = fmts.type_error(None, (int, str))
        asserts.equal(expected, obtained)

    @testing.subjects(fmts.underlined_title)
    def test_underlined_title(self):
        expected = "Title\n-----"
        obtained = fmts.underlined_title("Title")
        asserts.equal(expected, obtained)
