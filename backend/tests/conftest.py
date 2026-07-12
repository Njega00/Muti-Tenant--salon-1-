import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db import connection


@pytest.fixture(scope="session")
def test_engine():
	"""Create a fresh in-memory SQLite engine for the whole test session."""
	engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
	# Create all tables defined on the project's Base
	connection.Base.metadata.create_all(bind=engine)
	return engine


@pytest.fixture(scope="function")
def db(test_engine):
	"""Provide a transactional session and rollback after each test.

	Uses a SAVEPOINT / nested transaction pattern so tests can `commit()`
	freely while the outer transaction is rolled back at teardown.
	"""
	connection = test_engine.connect()
	transaction = connection.begin()

	TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
	db = TestingSessionLocal()
	try:
		yield db
	finally:
		db.close()
		transaction.rollback()
		connection.close()


@pytest.fixture(scope="function")
def client(db):
	"""Create a TestClient that uses the `db` fixture via dependency override."""

	def _override_get_db():
		try:
			yield db
		finally:
			pass

	app.dependency_overrides[connection.get_db] = _override_get_db

	with TestClient(app) as c:
		yield c
