from aamm import testing
from aamm.testing import asserts


class TestTestSuite(testing.TestSuite):
    @testing.subjects(testing.subjects)
    def test_subjects(self):
        def f():
            pass

        class FakeTestSuite(testing.TestSuite):
            @testing.subjects(f)
            def test_1(self):
                pass

        testing.TestSuite.registry.remove(FakeTestSuite)

        test = tuple(FakeTestSuite.run())[0]
        f_id = next(iter(test.subjects))

        asserts.equal(id(f), f_id)

    @testing.subjects(testing.tag)
    def test_tags(self):
        class FakeTestSuite(testing.TestSuite):
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

        testing.TestSuite.registry.remove(FakeTestSuite)

        tests = list(FakeTestSuite.run())

        # Get tagless tests only.
        filtered_tests = [t for t in tests if not t.tags]
        asserts.equal(1, len(filtered_tests))
        asserts.equal("test_1", filtered_tests[0].test.__name__)

        # Get tests without the "Skip" tag.
        filtered_tests = [t for t in tests if "Skip" not in t.tags]
        asserts.equal(3, len(filtered_tests))

        # Get tests with at least 2 tags.
        filtered_tests = [t for t in tests if len(t.tags) > 1]
        asserts.equal(1, len(filtered_tests))
        asserts.equal("test_4", filtered_tests[0].test.__name__)

    @testing.subjects(
        testing.TestSuite.__init_subclass__.__func__,
        testing.TestSuite.after,
        testing.TestSuite.before,
        testing.TestSuite.count_tests.__func__,
        testing.TestSuite.initialize.__func__,
        testing.TestSuite.registry,
        testing.TestSuite.run.__func__,
        testing.TestSuite.terminate.__func__,
    )
    def test_test_suite(self):
        # Create a fake `TestSuite` subclass to use its `run` class method later.
        class FakeTestSuite(testing.TestSuite):
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
                assert False

            def test_2(self):
                pass

            def test_3(self):
                pass

        asserts.contain(testing.TestSuite.registry, FakeTestSuite)
        testing.TestSuite.registry.remove(FakeTestSuite)

        registry = []

        # When `tests` gets run `registry` will be populated.
        for _ in FakeTestSuite.run():
            pass

        # Expect a particular sequence of letters.
        asserts.equal(list("ibababat"), registry)
