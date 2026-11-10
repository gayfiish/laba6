from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello() -> dict[str, str]:
    """Return a greeting from FastAPI."""
    return {"message": "Привет, FastAPI!"}