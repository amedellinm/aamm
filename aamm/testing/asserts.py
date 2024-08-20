def contain(a, b):
    assert b in a, f"assert {b!r} in {a!r}"


def equal(a, b):
    assert a == b, f"assert {a!r} == {b!r}"


def false(a):
    assert not a, f"assert not bool({a!r})"


def greater_equal(a, b):
    assert a >= b, f"assert {a!r} >= {b!r}"


def greater_than(a, b):
    assert a > b, f"assert {a!r} > {b!r}"


def less_equal(a, b):
    assert a <= b, f"assert {a!r} <= {b!r}"


def less_than(a, b):
    assert a < b, f"assert {a!r} < {b!r}"


def same(a, b):
    assert a is b, f"assert {a!r} is {b!r}"


def true(a):
    assert a, f"assert bool({a!r})"
