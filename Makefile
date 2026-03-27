.PHONY: help up down logs build clean

help:
	@echo "Available commands:"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs from all services"
	@echo "  make build    - Build all services"
	@echo "  make clean    - Remove all containers and volumes"
	@echo "  make backend-shell - Open shell in backend container"
	@echo "  make frontend-logs  - View frontend logs"

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

build:
	docker-compose build

clean:
	docker-compose down -v

backend-shell:
	docker-compose exec backend /bin/bash

frontend-logs:
	docker-compose logs -f frontend
