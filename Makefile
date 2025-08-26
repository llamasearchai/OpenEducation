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
