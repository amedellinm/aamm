from aamm import rng, testing
from aamm.testing import asserts


class TestRNG(testing.TestSuite):
    @testing.subjects(
        rng.create_state,
        rng.RNG.__init__,
        rng.RNG.get_state,
        rng.RNG.seed,
        rng.RNG.set_state,
    )
    def test_state(self):
        seed = 64
        a = rng.RNG(seed)
        b = rng.RNG()
        b.set_state(rng.create_state(seed))

        asserts.equal(a.get_state(), b.get_state())

        with asserts.exception_context(AttributeError):
            a.seed = 0
