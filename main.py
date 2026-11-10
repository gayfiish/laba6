from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello() -> dict[str, str]:
    """Return a greeting from FastAPI."""
    return {"message": "Привет, FastAPI!"}


@app.get("/greet")
def greet(name: str) -> dict[str, str]:
    """Return a personalized greeting."""
    return {"message": f"Привет, {name}!"}