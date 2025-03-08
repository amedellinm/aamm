from aamm import testing
from aamm.testing import asserts
from aamm.testing.core import FakeTestSuite, get_tags, test_suite_registry


class TestTestSuite(testing.TestSuite):
    def test_setup_and_teardown(self):
        # Create a fake `TestSuite` subclass to use its `run` class method later.
        class FTS(FakeTestSuite):
            def after(self):
                registry.append("a")

            def before(self):
                registry.append("b")

            @classmethod
            def initialize(cls):
                registry.append("i")

            @classmethod
            def terminate(cls):
                registry.append("t")

            def test_1(self):
                # `after` and `terminate` run even if test failure.
                raise AssertionError()

            def test_2(self):
                pass

            def test_3(self):
                pass

        registry = []

        tests = FTS.collect_tests()

        # When `tests` gets run `registry` will be populated.
        FTS.run(tests)

        # Expect a particular sequence of letters.
        asserts.equal(list("ibababat"), registry)

    def test_suite_registration(self):
        class TestSuite(testing.TestSuite):
            pass

        class MyTestSuite(testing.TestSuite):
            pass

        # The special name "TestSuite" is never registered.
        asserts.not_contain(test_suite_registry, TestSuite)

        # Any other name is.
        asserts.contain(test_suite_registry, MyTestSuite)
        test_suite_registry.remove(MyTestSuite)

    def test_tags(self):
        class FTS(FakeTestSuite):
            def test_1(self):
                pass

            @testing.tag("A")
            def test_2(self):
                pass

            @testing.tag("B")
            def test_3(self):
                pass

            # `test_4` is sad because it will be skipped. In actuality, the sad face is
            # important to test multi-tagging. Dw, it is all in the name of science.
            @testing.tag("Skip", ":(")
            def test_4(self):
                pass

        tests = FTS.collect_tests()

        # Get tagless tests only.
        filtered_tests = [t for t in tests if not get_tags(t)]
        asserts.equal(1, len(filtered_tests))
        asserts.equal("test_1", filtered_tests[0].test_name)

        # Get tests without the "Skip" tag.
        filtered_tests = [t for t in tests if "Skip" not in get_tags(t)]
        asserts.equal(3, len(filtered_tests))

        # Get tests with at least 2 tags.
        filtered_tests = [t for t in tests if len(get_tags(t)) > 1]
        asserts.equal(1, len(filtered_tests))
        asserts.equal("test_4", filtered_tests[0].test_name)
