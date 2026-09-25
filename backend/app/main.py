"""Application entry point: creates the FastAPI app, wires up CORS and routers."""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers import tickets

load_dotenv()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()  # create tables on startup if they don't exist
    yield


app = FastAPI(title="Customer Support CRM API", version="1.0.0", lifespan=lifespan)

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)

app.include_router(tickets.router)


@app.exception_handler(RequestValidationError)
def validation_error_handler(_request, exc: RequestValidationError):
    # Pydantic's default error payload is verbose; simplify it to {field, message} pairs.
    errors = [
        {"field": ".".join(str(p) for p in e["loc"] if p != "body"), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


@app.exception_handler(Exception)
def unhandled_error_handler(_request, exc: Exception):
    # Never leak stack traces to the client; the real error still goes to server logs.
    print(f"Unhandled error: {exc!r}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health():
    return {"status": "ok"}
