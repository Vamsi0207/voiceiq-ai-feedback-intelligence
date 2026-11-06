import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database.session import Base, get_db
from app.main import app
import app.main as main
import app.services.analysis as analysis


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite:///" + str(tmp_path / "test.db"),
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    sessions = sessionmaker(engine, expire_on_commit=False)

    def db():
        with sessions() as session:
            yield session

    app.dependency_overrides[get_db] = db
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setattr(main, "SessionLocal", sessions)
    monkeypatch.setattr(analysis, "SessionLocal", sessions)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()
