BASE_IMAGE=base
BASE_DOCKERFILE=Dockerfile.base

check-base:
	@echo "Проверка наличия базового образа $(BASE_IMAGE)..."
	@if docker inspect --type=image $(BASE_IMAGE) &> /dev/null; then \
		echo "Образ $(BASE_IMAGE) найден"; \
	else \
		echo "Сборка образа $(BASE_IMAGE)"; \
		docker build -t $(BASE_IMAGE) -f $(BASE_DOCKERFILE) .; \
	fi

base:
	@echo "Проверка наличия базового образа $(BASE_IMAGE)..."
	@if docker inspect --type=image $(BASE_IMAGE) &> /dev/null; then \
		docker rmi $(BASE_IMAGE); \
	docker build -t $(BASE_IMAGE) -f $(BASE_DOCKERFILE) .; \
	fi

build: check-base
	docker-compose build

start:
	docker-compose up -d

up: build start

stop:
	docker-compose stop

clean: stop
	docker system prune -f

logs:
	docker-compose logs -f

down:
	docker-compose down

restart: down build start