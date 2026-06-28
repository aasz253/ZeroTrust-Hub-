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
        role = Role(name="admin", description="Admin")
        db.add(role)
        db.flush()
        db.add(User(
            email="admin@test.com",
            username="admin",
            hashed_password=hash_password("Admin123!"),
            role_id=role.id,
        ))
        db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def get_token():
    resp = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin123!",
    })
    return resp.json()["access_token"]


def test_dashboard_requires_auth():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 401


def test_dashboard_authenticated():
    token = get_token()
    response = client.get("/api/dashboard/stats", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert "threat_score" in data


def test_threats_list():
    token = get_token()
    response = client.get("/api/threats", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert "items" in response.json()


def test_cves_search():
    token = get_token()
    response = client.get("/api/cves", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert "items" in response.json()
