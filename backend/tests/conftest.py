import os

# Must be set before the application is imported anywhere in the test run.
os.environ.setdefault('JWT_SECRET', 'TEST_ONLY_NOT_FOR_DEPLOYMENT_SECRET_12345678901234567890')

import pytest

from app.core.ratelimit import reset_rate_limits


@pytest.fixture(autouse=True)
def clear_rate_limits():
    """Rate-limit counters are process-wide, so isolate every test."""
    reset_rate_limits()
    yield
    reset_rate_limits()