from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    """Display the form and process the submitted name."""
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


if __name__ == "__main__":
    app.run(debug=True)