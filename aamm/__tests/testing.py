from aamm import testing
from aamm.testing import asserts
from aamm.testing.core import FakeTestSuite, Test, get_tags, test_suite_registry
from aamm.testing.validate import all_equal


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

        _, tests = FTS.collect_tests()

        # When `tests` gets run `registry` will be populated.
        FTS.run(tests)

        # Expect a particular sequence of letters.
        asserts.equal(list("ibababat"), registry)

    def test_shuffle_seed(self):
        TEST_NAMES = "0123456789"
        ITERATIONS = 10

        # Create a list of fake tests. Usually, this would be declared inside the test
        # suite using the `def` keyword.
        tests = [Test("", "", char, lambda: None) for char in TEST_NAMES]

        fixed_seed = []
        none_seed = []

        for _ in range(ITERATIONS):
            # Given the same input and seed, tests run in the same order every time.
            tests_copy = tests.copy()
            testing.TestSuite.run(tests_copy, seed=0)
            fixed_seed.append("".join(t.test_name for t in tests_copy))

            # Given the same input but different seed, run order should vary.
            tests_copy = tests.copy()
            testing.TestSuite.run(tests_copy, seed=None)
            none_seed.append("".join(t.test_name for t in tests_copy))

        asserts.true(all_equal(fixed_seed))
        asserts.false(all_equal(none_seed))

    def test_suite_registration(self):
        class TestSuite(testing.TestSuite):
            pass

        class MyTestSuite(testing.TestSuite):
            pass

        # The special name "TestSuite" is never registered.
        asserts.false(TestSuite in test_suite_registry)

        # Any other name is.
        asserts.true(MyTestSuite in test_suite_registry)
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

        _, tests = FTS.collect_tests()

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
