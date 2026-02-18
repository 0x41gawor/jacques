APP_NAME=jacques-identity-api
PORT?=$(BANDARI)

.PHONY: build run dev docker-build docker-run docker-stop docker-restart

# ---------- LOCAL ----------

build:
	pip install ../../common
	pip install .

run:
	python3 -m app.main

dev: build run

# ---------- DOCKER ----------

docker-build:
	docker build -f Dockerfile -t $(APP_NAME):latest ../..

docker-run:
	docker run -d --name $(APP_NAME) \
		--add-host=host.docker.internal:host-gateway \
		-p $(PORT):5000 \
		--env-file ../../.env \
		--env NOME \
		--env AGANDSKODE \
		--env THAREUX \
		--env DB_HOST=host.docker.internal \
		$(APP_NAME):latest

docker-stop:
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true

docker-restart: docker-stop docker-run
