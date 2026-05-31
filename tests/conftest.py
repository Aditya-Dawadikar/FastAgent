import pytest
import fastagent


@pytest.fixture(autouse=True)
def fresh_run_context():
    """Give every test its own isolated FastAgent execution context."""
    token = fastagent.new_run_context()
    yield
    fastagent.reset_run_context(token)
