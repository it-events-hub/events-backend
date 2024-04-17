startapp:
	cd src; python3 manage.py startapp <name>

run:
	cd src; python3 manage.py runserver

makemig:
	cd src; python3 manage.py makemigrations

makemig-users:
	cd src; python3 manage.py makemigrations users

migrate:
	cd src; python3 manage.py migrate

superuser:
	cd src; python3 manage.py createsuperuser --email test@test.com --phone 88008888888 --first_name Ad --last_name Min -v 3

superuser-empty:
	cd src; python3 manage.py createsuperuser

shell:
	cd src; python3 manage.py shell

dumpdb:
	cd src; python3 manage.py dumpdata --output dump.json

loaddb:
	cd src; python3 manage.py loaddata dump.json

loaddb-no-contenttypes:
	cd src; python3 manage.py loaddata --exclude contenttypes dump.json

loaddb-no-contenttypes-permissions:
	cd src; python3 manage.py loaddata --exclude contenttypes --exclude auth.permission dump.json

load_csv:
	cd src; python3 manage.py load_csv

collectstatic:
	cd src; python3 manage.py collectstatic --no-input

up-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml up -d --remove-orphans

build-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml up -d --build --remove-orphans

stop-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml stop

start-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml start

makemig-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml exec -it backend python manage.py makemigrations

migrate-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml exec -it backend python manage.py migrate

superuser-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml exec -it backend python manage.py createsuperuser --email test@test.com --username admin -v 3

collectstatic-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml exec -it backend python manage.py collectstatic --no-input

shell-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml exec -it backend python manage.py shell

ls-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml exec -it backend ls

dumpdb-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml exec -it backend python3 manage.py dumpdata --output dump.json

loaddb-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml exec -it backend python3 manage.py loaddata dump.json

loaddb-no-contenttypes-compose:
	cd infra; sudo docker compose -f docker-compose.local.yml exec -it backend python3 manage.py loaddata --exclude contenttypes dump.json

prune-containers:
	sudo docker container prune

prune-images:
	sudo docker image prune

celery-worker:
	cd src; python3 -m celery -A config.celery.app worker -l info

logs-backend:
	sudo docker logs --tail 50 --follow --timestamps backend

logs-nginx:
	sudo docker logs --tail 50 --follow --timestamps nginx

logs-db:
	sudo docker logs --tail 50 --follow --timestamps db

logs-redis:
	sudo docker logs --tail 50 --follow --timestamps funtech_redis

logs-celery-worker:
	sudo docker logs --tail 50 --follow --timestamps funtech_celery_worker
