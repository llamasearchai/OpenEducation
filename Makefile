PY=python

.PHONY: run dev docker up smoke

run:
	uvicorn app.main:app --reload --port 8000

smoke:
	$(PY) scripts/smoke_test.py --base http://localhost:8000

check-secrets:
	$(PY) scripts/check_secrets.py

docker:
	docker build -t openedu-app:latest .

up:
	docker compose up --build

publish:
	bash scripts/publish.sh

venv:
	python -m venv .venv && . .venv/bin/activate && python -m pip install -U pip setuptools wheel

install:
	. .venv/bin/activate && pip install -r requirements.txt && pip install ruff mypy tox hatch

test:
	. .venv/bin/activate && pytest -q

lint:
	. .venv/bin/activate && ruff check .

types:
	. .venv/bin/activate && mypy .
