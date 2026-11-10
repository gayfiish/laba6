
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import flask_app
from main import app as fastapi_app

api_client = TestClient(fastapi_app)
flask_client = flask_app.app.test_client()


def test_fastapi_hello() -> None:
    """Check the FastAPI hello endpoint."""
    response = api_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Привет, FastAPI!"}


def test_fastapi_greet() -> None:
    """Check a personalized greeting."""
    response = api_client.get("/greet", params={"name": "Анастасия"})
    assert response.status_code == 200
    assert response.json() == {"message": "Привет, Анастасия!"}


def test_fastapi_another_name() -> None:
    """Check another name."""
    response = api_client.get("/greet", params={"name": "Иван"})
    assert response.status_code == 200
    assert response.json() == {"message": "Привет, Иван!"}


def test_fastapi_missing_name() -> None:
    """Check validation of a missing parameter."""
    response = api_client.get("/greet")
    assert response.status_code == 422


def test_flask_get_form() -> None:
    """Check that the HTML form is displayed."""
    response = flask_client.get("/")
    assert response.status_code == 200
    assert "Форма приветствия" in response.get_data(as_text=True)


def test_flask_greeting() -> None:
    """Check form submission."""
    response = flask_client.post("/", data={"name": "Анастасия"})
    assert response.status_code == 200
    assert "Привет, Анастасия!" in response.get_data(as_text=True)


def test_flask_empty_name() -> None:
    """Check an empty submitted name."""
    response = flask_client.post("/", data={"name": "   "})
    assert response.status_code == 200
    assert "Введите имя." in response.get_data(as_text=True)


def test_upload_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Check that an uploaded file is saved."""
    monkeypatch.setattr(flask_app, "UPLOAD_FOLDER", tmp_path)

    response = flask_client.post(
        "/upload",
        data={"file": (BytesIO(b"Hello"), "test.txt")},
    )

    assert response.status_code == 200
    assert "успешно загружен" in response.get_data(as_text=True)

    files = list(tmp_path.glob("*.txt"))
    assert len(files) == 1
    assert files[0].read_bytes() == b"Hello"


def test_upload_invalid_extension(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Check rejection of unsupported file types."""
    monkeypatch.setattr(flask_app, "UPLOAD_FOLDER", tmp_path)

    response = flask_client.post(
        "/upload",
        data={"file": (BytesIO(b"Test"), "test.exe")},
    )

    assert response.status_code == 400
    assert "Недопустимый формат" in response.get_data(as_text=True)
    assert list(tmp_path.iterdir()) == []


def test_upload_missing_file() -> None:
    """Check a request without a file."""
    response = flask_client.post("/upload", data={})
    assert response.status_code == 400
    assert "Выберите файл." in response.get_data(as_text=True)


def test_upload_too_large() -> None:
    """Check the upload size limit."""
    large_file = BytesIO(b"x" * (5 * 1024 * 1024 + 1))

    response = flask_client.post(
        "/upload",
        data={"file": (large_file, "large.txt")},
    )

    assert response.status_code == 413
    assert "превышает 5 МБ" in response.get_data(as_text=True)
