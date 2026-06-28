import pytest
from fastapi.testclient import TestClient
from main import app
from app.database.session import Base, engine, SessionLocal
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(Role).first():
        admin_role = Role(name="admin", description="Admin")
        analyst_role = Role(name="analyst", description="Analyst")
        db.add(admin_role)
        db.add(analyst_role)
        db.flush()
        db.add(User(
            email="test@test.com",
            username="test",
            hashed_password=hash_password("Test1234!"),
            role_id=analyst_role.id,
        ))
        db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_login_success():
    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "Test1234!",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid():
    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "wrong",
    })
    assert response.status_code == 401


def test_register():
    response = client.post("/api/auth/register", json={
        "email": "new@test.com",
        "username": "newuser",
        "password": "NewUser123!",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
