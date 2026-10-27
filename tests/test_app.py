from fact_checker import app


def test_rate_limit_is_per_ip():
    assert all(app.allow("1.1.1.1") for _ in range(app.PER_IP_HOURLY))
    assert not app.allow("1.1.1.1")
    assert app.allow("2.2.2.2")
