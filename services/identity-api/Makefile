APP_NAME=jacques-identity-api
PORT?=$(BANDARI)

build:
	pip install -e .

run:
	python -m app.main

docker-build:
	docker build -t $(APP_NAME):latest .

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