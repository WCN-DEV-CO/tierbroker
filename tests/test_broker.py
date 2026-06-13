import time
from tierbroker import Broker, Provider, NoProviderAvailable


def test_round_robin_spreads_load():
    calls = {"a": 0, "b": 0}
    b = Broker(max_retries=1)
    b.add(Provider("a", lambda j: calls.__setitem__("a", calls["a"] + 1), weight=1))
    b.add(Provider("b", lambda j: calls.__setitem__("b", calls["b"] + 1), weight=1))
    for _ in range(10):
        b.submit("job")
    # both providers should have shared the load
    assert calls["a"] > 0 and calls["b"] > 0
    assert abs(calls["a"] - calls["b"]) <= 2


def test_quota_exhaustion():
    b = Broker(max_retries=1)
    b.add(Provider("only", lambda j: "ok", quota=3))
    for _ in range(3):
        assert b.submit("j") == "ok"
    try:
        b.submit("j")
        assert False, "should have raised"
    except NoProviderAvailable:
        pass


def test_failover_on_error():
    def bad(j):
        raise RuntimeError("down")
    b = Broker(max_retries=3, backoff_base=0.001)
    b.add(Provider("bad", bad, weight=5))
    b.add(Provider("good", lambda j: "recovered", weight=1))
    assert b.submit("j") == "recovered"


def test_stats():
    b = Broker(max_retries=1)
    b.add(Provider("p", lambda j: "ok", quota=10))
    b.submit("j")
    s = b.stats()
    assert s["p"]["used"] == 1
    assert s["p"]["exhausted"] is False


if __name__ == "__main__":
    test_round_robin_spreads_load()
    test_quota_exhaustion()
    test_failover_on_error()
    test_stats()
    print("all tests passed")
