import sys
import os
import pytest

# Add the parent folder (vote/) to sys.path so app.py is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app  # noqa: E402


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_home_get_request(client):
    """GET / should return status 200."""
    response = client.get("/")
    assert response.status_code == 200

