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

collectstatic:
	cd src; python3 manage.py collectstatic --no-input
