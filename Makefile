dc = docker-compose -f docker-compose.yml
user_id:=$(shell id -u)
group_id:=$(shell id -g)

build:
	$(dc) build --build-arg UID=$(user_id) --build-arg GID=$(group_id)

migrate:
	$(dc) run --rm backend python manage.py migrate $(revert)

run:
	$(dc) up -d backend nginx

up:
	$(dc) up backend nginx

delete-db:
	$(dc) stop postgres adminer
	$(dc) rm -v postgres
	$(dc) up -d postgres adminer
	sleep 2

recreate-db: delete-db migrate

migrations:
	$(dc) run --rm backend python manage.py makemigrations $(add)

logs:
	$(dc) logs -f

black:
	$(dc) run --rm backend black .

isort:
	$(dc) run --rm backend isort .

format: isort black

test:
	pytest .