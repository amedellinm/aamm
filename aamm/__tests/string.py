from aamm import file_system as fs
from aamm import string, testing
from aamm.testing import asserts


class TestRNG(testing.TestSuite):
    @testing.subjects(string.create_matcher)
    def test_matcher(self):
        """
        Several `string` symbols were created by `string.create_matcher`.
        The tests of said symbols indirectly test `string.create_matcher`.

        """

    @testing.subjects(string.indent)
    def test_indent(self):
        with open(fs.here("string", "indent.txt")) as file:
            text, expected = file.read().split("\n\n")

        obtained = string.indent(text)
        asserts.equal(expected, obtained)

    @testing.subjects(string.is_camelcase)
    def test_is_camelcase(self):
        assert string.is_camelcase("camelcasE")
        assert string.is_camelcase("camelCase")
        assert string.is_camelcase("camelCasE")
        assert not string.is_camelcase("_camelCase")
        assert not string.is_camelcase("camel_case")
        assert not string.is_camelcase("camelCAse")
        assert not string.is_camelcase("CamelCase")
        assert not string.is_camelcase("CAMELCASE")

    @testing.subjects(string.is_dunder)
    def test_is_dunder(self):
        assert string.is_dunder("___dunder___")
        assert string.is_dunder("__dunder__")
        assert string.is_dunder("__dx__")
        assert string.is_dunder("__x__")
        assert not string.is_dunder("__dunder_")
        assert not string.is_dunder("__dunder")
        assert not string.is_dunder("_dunder__")
        assert not string.is_dunder("_dunder_")
        assert not string.is_dunder("dunder__")

    @testing.subjects(string.is_lowercase)
    def test_is_lowercase(self):
        assert string.is_lowercase("lowercase")
        assert not string.is_lowercase("lower_case")
        assert not string.is_lowercase("Lowercase")
        assert not string.is_lowercase("1owercase")

    @testing.subjects(string.is_snakecase)
    def test_is_snakecase(self):
        assert string.is_snakecase("snake_case")
        assert not string.is_snakecase("Snake_case")
        assert not string.is_snakecase("snake_Case")
        assert not string.is_snakecase("SNAKE_CASE")
        assert not string.is_snakecase("snake-case")
        assert not string.is_snakecase("snakecase")

    @testing.subjects(string.is_titlecase)
    def test_is_titlecase(self):
        assert string.is_titlecase("TitleCase")
        assert string.is_titlecase("Titlecase")
        assert string.is_titlecase("TitleCasE")
        assert not string.is_titlecase("titleCase")
        assert not string.is_titlecase("Tit1eCase")
        assert not string.is_titlecase("Title_Case")

    @testing.subjects(string.is_uppercase)
    def test_is_uppercase(self):
        assert string.is_uppercase("UPPERCASE")
        assert not string.is_uppercase("UPPER_CASE")
        assert not string.is_uppercase("UPPERCA5E")
        assert not string.is_uppercase("UpPERCASE")

    @testing.subjects(string.is_utf8_valid)
    def test_is_utf8_valid(self):
        """Based on `str.encode`."""

    @testing.subjects(string.right_replace)
    def test_right_replace(self):
        obtained = string.right_replace("___.__._.._", ".", "_", 3)
        expected = "___._______"
        asserts.equal(expected, obtained)

    @testing.subjects(string.wrap)
    def test_wrap(self):
        """Based on `textwrap`."""
