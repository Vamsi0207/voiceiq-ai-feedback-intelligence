from contextlib import asynccontextmanager
import logging
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import update
from app.database.session import Base, engine, SessionLocal
from app.models.entities import Job
from app.core.config import settings
from app.api.routes import router


class StructuredFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "level": record.levelname,
                "logger": record.name,
                "event": record.getMessage(),
                "error_type": getattr(record, "error_type", None),
                "job_id": getattr(record, "job_id", None),
            }
        )


handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logging.getLogger("voiceiq").addHandler(handler)
logging.getLogger("voiceiq").propagate = False


@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        db.execute(
            update(Job)
            .where(Job.status.in_(["queued", "running"]))
            .values(
                status="failed",
                error="Server restarted during analysis. Retry analysis.",
            )
        )
        db.commit()
    yield


app = FastAPI(title="VoiceIQ API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(router)


@app.exception_handler(Exception)
async def unexpected(request: Request, exc: Exception):
    logging.getLogger("voiceiq").error(
        "request_failed", extra={"error_type": type(exc).__name__}
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal operation failed. Check the service configuration and try again."
        },
    )
