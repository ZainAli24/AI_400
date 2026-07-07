import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import time

from refresher_dep import app, connect_db


client = TestClient(app)



def fake_db():
    print("Connection Fake DB ....")
    time.sleep(4)
    return {"message": "Connected Test DB successfully!", "fake_db_status": "OK"}



def test_start_db():
    app.dependency_overrides[connect_db] = fake_db

    res = client.get("/connect")
    assert res.status_code == 200
    assert res.json() == {"DB_LOGS": {"message": "Connected Test DB successfully!", "fake_db_status": "OK"}}

    app.dependency_overrides.clear()
