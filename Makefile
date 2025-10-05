.DEFAULT_GOAL := help

help:
	@echo "make build  - Build the image"
	@echo "make up     - Start API + Mongo (creates .env if missing)"
	@echo "make down   - Stop services"
	@echo "make logs   - View API logs"

build:
	docker compose build

up:
	cp -n .env.example .env || true
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f api
