from aamm import file_system as fs
from aamm import strings, testing
from aamm.testing import asserts


class TestRNG(testing.TestSuite):
    @testing.subjects(strings.create_matcher)
    def test_matcher(self):
        """
        Several `string` symbols were created by `string.create_matcher`.
        The tests of said symbols indirectly test `string.create_matcher`.

        """

    @testing.subjects(strings.indent)
    def test_indent(self):
        with open(fs.here("string", "indent.txt")) as file:
            text, expected = file.read().split("\n\n")

        obtained = strings.indent(text)
        asserts.equal(expected, obtained)

    @testing.subjects(strings.is_camelcase)
    def test_is_camelcase(self):
        assert strings.is_camelcase("camelcasE")
        assert strings.is_camelcase("camelCase")
        assert strings.is_camelcase("camelCasE")
        assert not strings.is_camelcase("_camelCase")
        assert not strings.is_camelcase("camel_case")
        assert not strings.is_camelcase("camelCAse")
        assert not strings.is_camelcase("CamelCase")
        assert not strings.is_camelcase("CAMELCASE")

    @testing.subjects(strings.is_dunder)
    def test_is_dunder(self):
        assert strings.is_dunder("___dunder___")
        assert strings.is_dunder("__dunder__")
        assert strings.is_dunder("__dx__")
        assert strings.is_dunder("__x__")
        assert not strings.is_dunder("__dunder_")
        assert not strings.is_dunder("__dunder")
        assert not strings.is_dunder("_dunder__")
        assert not strings.is_dunder("_dunder_")
        assert not strings.is_dunder("dunder__")

    @testing.subjects(strings.is_lowercase)
    def test_is_lowercase(self):
        assert strings.is_lowercase("lowercase")
        assert not strings.is_lowercase("lower_case")
        assert not strings.is_lowercase("Lowercase")
        assert not strings.is_lowercase("1owercase")

    @testing.subjects(strings.is_snakecase)
    def test_is_snakecase(self):
        assert strings.is_snakecase("snake_case")
        assert not strings.is_snakecase("Snake_case")
        assert not strings.is_snakecase("snake_Case")
        assert not strings.is_snakecase("SNAKE_CASE")
        assert not strings.is_snakecase("snake-case")
        assert not strings.is_snakecase("snakecase")

    @testing.subjects(strings.is_titlecase)
    def test_is_titlecase(self):
        assert strings.is_titlecase("TitleCase")
        assert strings.is_titlecase("Titlecase")
        assert strings.is_titlecase("TitleCasE")
        assert not strings.is_titlecase("titleCase")
        assert not strings.is_titlecase("Tit1eCase")
        assert not strings.is_titlecase("Title_Case")

    @testing.subjects(strings.is_uppercase)
    def test_is_uppercase(self):
        assert strings.is_uppercase("UPPERCASE")
        assert not strings.is_uppercase("UPPER_CASE")
        assert not strings.is_uppercase("UPPERCA5E")
        assert not strings.is_uppercase("UpPERCASE")

    @testing.subjects(strings.is_utf8_valid)
    def test_is_utf8_valid(self):
        """Based on `str.encode`."""

    @testing.subjects(strings.right_replace)
    def test_right_replace(self):
        obtained = strings.right_replace("___.__._.._", ".", "_", 3)
        expected = "___._______"
        asserts.equal(expected, obtained)

    @testing.subjects(strings.wrap)
    def test_wrap(self):
        """Based on `textwrap`."""
