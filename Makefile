.PHONY: help start-ollama stop-ollama restart-ollama pull-model delete-model list-models show-model pull-phi3 pull-llama2 pull-llama3 pull-mistral pull-codegemma pull-deepseek pull-qwen clean-models start-db stop-db db-init db-reset start-all stop-all

# Default target
help:
	@echo "Symbiote - Ollama Model Management"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "Docker Services:"
	@echo "  make start-all             - Start all services (Ollama + PostgreSQL)"
	@echo "  make stop-all              - Stop all services"
	@echo "  make start-ollama          - Start Ollama Docker container"
	@echo "  make stop-ollama           - Stop Ollama Docker container"
	@echo "  make restart-ollama        - Restart Ollama Docker container"
	@echo "  make start-db              - Start PostgreSQL Docker container"
	@echo "  make stop-db               - Stop PostgreSQL Docker container"
	@echo ""
	@echo "Database:"
	@echo "  make db-init               - Initialize database tables"
	@echo "  make db-reset              - Reset database (WARNING: drops all data)"
	@echo ""
	@echo "Model Management:"
	@echo "  make list-models           - List all installed models"
	@echo "  make pull-model MODEL=name - Pull a specific model (e.g., MODEL=phi3)"
	@echo "  make delete-model MODEL=name - Delete a specific model"
	@echo "  make show-model MODEL=name - Show information about a model"
	@echo ""
	@echo "Quick pull commands:"
	@echo "  make pull-phi3             - Pull phi3 model"
	@echo "  make pull-llama2           - Pull llama2 model"
	@echo "  make pull-llama3           - Pull llama3 model"
	@echo "  make pull-mistral          - Pull mistral model"
	@echo "  make pull-codegemma        - Pull codegemma model"
	@echo "  make pull-deepseek         - Pull deepseek-coder model"
	@echo "  make pull-qwen             - Pull qwen model"
	@echo ""
	@echo "  make clean-models          - Remove all models (WARNING: destructive)"

# Docker Compose commands - All services
start-all:
	@echo "Starting all services (Ollama + PostgreSQL)..."
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "Services running:"
	@echo "  - Ollama: http://localhost:11434"
	@echo "  - PostgreSQL: localhost:5432"

stop-all:
	@echo "Stopping all services..."
	docker-compose down
	@echo "All services stopped"

# Ollama commands
start-ollama:
	@echo "Starting Ollama container..."
	docker-compose up -d ollama
	@echo "Waiting for Ollama to be ready..."
	@sleep 3
	@echo "Ollama is running at http://localhost:11434"

stop-ollama:
	@echo "Stopping Ollama container..."
	docker-compose stop ollama
	@echo "Ollama stopped"

restart-ollama: stop-ollama start-ollama
	@echo "Ollama restarted"

# Database commands
start-db:
	@echo "Starting PostgreSQL container..."
	docker-compose up -d postgres
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 3
	@echo "PostgreSQL is running at localhost:5432"

stop-db:
	@echo "Stopping PostgreSQL container..."
	docker-compose stop postgres
	@echo "PostgreSQL stopped"

db-init:
	@echo "Initializing database tables..."
	uv run python -c "from src.db import init_db; init_db()"
	@echo "Database initialized"

db-reset:
	@echo "WARNING: This will drop all database tables and data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Resetting database..."; \
		uv run python -c "from src.db import drop_db, init_db; drop_db(); init_db()"; \
		echo "Database reset complete"; \
	else \
		echo "Cancelled."; \
	fi

# Model management commands
list-models:
	@echo "Listing installed models..."
	@docker exec ollama ollama list || echo "Error: Ollama container is not running. Run 'make start-ollama' first."

pull-model:
	@if [ -z "$(MODEL)" ]; then \
		echo "Error: MODEL is required. Usage: make pull-model MODEL=phi3"; \
		exit 1; \
	fi
	@echo "Pulling model: $(MODEL)..."
	@docker exec ollama ollama pull $(MODEL) || echo "Error: Failed to pull model or Ollama is not running."

delete-model:
	@if [ -z "$(MODEL)" ]; then \
		echo "Error: MODEL is required. Usage: make delete-model MODEL=phi3"; \
		exit 1; \
	fi
	@echo "Deleting model: $(MODEL)..."
	@docker exec ollama ollama rm $(MODEL) || echo "Error: Failed to delete model or Ollama is not running."

show-model:
	@if [ -z "$(MODEL)" ]; then \
		echo "Error: MODEL is required. Usage: make show-model MODEL=phi3"; \
		exit 1; \
	fi
	@echo "Showing information for model: $(MODEL)..."
	@docker exec ollama ollama show $(MODEL) || echo "Error: Failed to show model or Ollama is not running."

# Quick pull commands for common models
pull-phi3:
	@$(MAKE) pull-model MODEL=phi3

pull-llama2:
	@$(MAKE) pull-model MODEL=llama2

pull-llama3:
	@$(MAKE) pull-model MODEL=llama3

pull-mistral:
	@$(MAKE) pull-model MODEL=mistral

pull-codegemma:
	@$(MAKE) pull-model MODEL=codegemma

pull-deepseek:
	@$(MAKE) pull-model MODEL=deepseek-coder

pull-qwen:
	@$(MAKE) pull-model MODEL=qwen

# Cleanup
clean-models:
	@echo "WARNING: This will remove ALL models from Ollama!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Removing all models..."; \
		docker exec ollama ollama list | grep -v "^NAME" | awk '{print $$1}' | xargs -I {} docker exec ollama ollama rm {} || echo "No models to remove or Ollama is not running."; \
	else \
		echo "Cancelled."; \
	fi

# Check Ollama status
status:
	@echo "Checking Ollama status..."
	@docker ps | grep ollama || echo "Ollama container is not running"
	@if docker ps | grep -q ollama; then \
		echo "Ollama is running"; \
		$(MAKE) list-models; \
	fi

