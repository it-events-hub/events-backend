run:
	cd src; python3 manage.py runserver

makemig:
	cd src; python3 manage.py makemigrations

makemig-users:
	cd src; python3 manage.py makemigrations users

migrate:
	cd src; python3 manage.py migrate

superuser:
	cd src; python3 manage.py createsuperuser --email test@test.com --username admin -v 3

superuser-empty:
	cd src; python3 manage.py createsuperuser

shell:
	cd src; python3 manage.py shell

dumpdb:
	cd src; python3 manage.py dumpdata --output dump.json

loaddb:
	cd src; python3 manage.py loaddata dump.json

loaddb-no-contenttypes-adminlogentry-permissions:
	cd src; python3 manage.py loaddata --exclude contenttypes --exclude admin.logentry --exclude auth.permission dump.json

collectstatic:
	cd src; python3 manage.py collectstatic --no-input
