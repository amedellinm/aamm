from aamm import testing
from aamm.testing import asserts
from aamm.testing.core import FakeTestSuite


class TestTestSuite(testing.TestSuite):
    @testing.subjects(testing.subjects)
    def test_subjects(self):
        def f():
            pass

        class FTS(FakeTestSuite):
            @testing.subjects(f)
            def test_1(self):
                pass

        test = FTS.collect_tests()[0]
        f_id = next(iter(test.subjects))

        asserts.equal(id(f), f_id)

    @testing.subjects(testing.tag)
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
        filtered_tests = [t for t in tests if not t.tags]
        asserts.equal(1, len(filtered_tests))
        asserts.equal("test_1", filtered_tests[0].test_name)

        # Get tests without the "Skip" tag.
        filtered_tests = [t for t in tests if "Skip" not in t.tags]
        asserts.equal(3, len(filtered_tests))

        # Get tests with at least 2 tags.
        filtered_tests = [t for t in tests if len(t.tags) > 1]
        asserts.equal(1, len(filtered_tests))
        asserts.equal("test_4", filtered_tests[0].test_name)
