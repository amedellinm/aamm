import aamm.testing.core as testing
from aamm.testing import asserts


class TestTestSuite(testing.TestSuite):
    @testing.subjects(
        testing.TestSuite.after,
        testing.TestSuite.before,
        testing.TestSuite.collect_tests.__func__,
        testing.TestSuite.initialize.__func__,
        testing.TestSuite.run.__func__,
        testing.TestSuite.terminate.__func__,
    )
    def test_setup_and_teardown(self):
        # Create a fake `TestSuite` subclass to use its `run` class method later.
        class FTS(testing.FakeTestSuite):
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

    @testing.subjects(testing.test_suite_registry)
    def test_suite_registration(self):
        class TestSuite(testing.TestSuite):
            pass

        class MyTestSuite(testing.TestSuite):
            pass

        # The special name "TestSuite" is never registered.
        asserts.not_contain(testing.test_suite_registry, TestSuite)

        # Any other name is.
        asserts.contain(testing.test_suite_registry, MyTestSuite)
        testing.test_suite_registry.remove(MyTestSuite)
