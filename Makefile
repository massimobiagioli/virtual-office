# Virtual Office everyday commands. Every target is a plain `docker compose` call with no
# logic of its own (DOCKER.md §6, ADR-0004); `make` alone prints the help.

COMPOSE := docker compose

.DEFAULT_GOAL := help
.PHONY: help up down logs status

help: ## Show this help
	@echo "Usage: make <target>"
	@echo ""
	@awk 'BEGIN { FS = ":.*## " } /^[a-z]+:.*## / { printf "  %-8s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

up: ## Build and start the stack in the background
	$(COMPOSE) up --build -d

down: ## Stop and remove the stack containers
	$(COMPOSE) down

logs: ## Follow the logs (one service: make logs s=core)
	$(COMPOSE) logs -f $(s)

status: ## Show the state of the services
	$(COMPOSE) ps
