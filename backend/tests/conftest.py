import pytest


@pytest.fixture
def test_db_path(tmp_path):
    return tmp_path / "test_app.db"


@pytest.fixture
def test_app(test_db_path, monkeypatch):
    monkeypatch.setattr("backend.models.db_connect.DB_NAME", str(test_db_path))
    from backend.app import create_app

    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(test_app):
    return test_app.test_client()


@pytest.fixture
def seeded_client(test_app):
    from backend.models.db_init import init_db

    init_db()
    return test_app.test_client()


@pytest.fixture
def logged_in_as(seeded_client):
    def _login(user_id):
        with seeded_client.session_transaction() as sess:
            sess["user_id"] = user_id
        return seeded_client

    return _login
