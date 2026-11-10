from __future__ import annotations
from pathlib import Path
from uuid import uuid4

from flask import Flask, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

UPLOAD_FOLDER = Path(__file__).resolve().parent / "uploads"
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg"}


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    """Display the greeting form and process the submitted name."""
    greeting = ""
    error = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()

        if name:
            greeting = f"Привет, {name}!"
        else:
            error = "Введите имя."

    return render_template(
        "index.html",
        greeting=greeting,
        error=error
    )


@app.post("/upload")
def upload_file() -> str | tuple[str, int]:
    """Validate and save a file uploaded through the form."""
    file = request.files.get("file")

    if file is None or not file.filename:
        return render_template(
            "index.html",
            upload_error="Выберите файл."
        ), 400

    original_name = Path(file.filename).name
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return render_template(
            "index.html",
            upload_error="Недопустимый формат файла."
        ), 400

    try:
        UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}{extension}"
        file.save(UPLOAD_FOLDER / filename)
    except OSError:
        app.logger.exception("File upload failed")
        return render_template(
            "index.html",
            upload_error="Не удалось сохранить файл."
        ), 500

    return render_template(
        "index.html",
        upload_message=f"Файл {original_name} успешно загружен!"
    )


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(error: RequestEntityTooLarge) -> tuple[str, int]:
    """Handle files exceeding the upload size limit."""
    return render_template(
        "index.html",
        upload_error="Размер файла превышает 5 МБ."
    ), 413


if __name__ == "__main__":
    app.run(debug=True)
