APP_NAME=ingestion-worker
PORT?=$(BANDARI)

.PHONY: build run dev docker-build docker-run docker-stop docker-restart

# ---------- LOCAL ----------

run:
	pwd
	python3 -m app.main --log-level DEBUG

dev: run