import aamm.testing.core as testing
from aamm import file_system as fs
from aamm.testing import asserts


class TestTestSuite(testing.TestSuite):
    @testing.subjects(
        testing.is_test_file,
        testing.main,
        testing.Test.__init__,
    )
    def test_core(self):
        """If this test runs, it passed."""

    @testing.subjects(testing.TEST_DIRECTORY_NAME, testing.test_file)
    def test_test_file(self):
        path = fs.join("aclib", "my_module.py")
        expected = fs.join("aclib", testing.TEST_DIRECTORY_NAME, "my_module.py")
        asserts.equal(expected, testing.test_file(path))

        path = fs.join("aclib", "my_module", "__init__.py")
        expected = fs.join(
            "aclib", "my_module", testing.TEST_DIRECTORY_NAME, "my_module.py"
        )
        asserts.equal(expected, testing.test_file(path))

    @testing.subjects(testing.TEST_PREFIX)
    def test_test_prefix(self):
        # Create a fake `TestSuite` subclass to use its `run` class method later.
        class FakeTestSuite(testing.TestSuite):
            def test_1(self):
                pass

            def test_2(self):
                pass

            def test3(self):
                pass

        testing.TestSuite.registry.remove(FakeTestSuite)

        asserts.equal(2, sum(1 for _ in FakeTestSuite.run()))
