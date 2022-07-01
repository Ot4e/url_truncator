init:
	cd truncat && sqlite3 truncat.sqlite < init.sql

dev:
	cd truncat && FLASK_APP=app FLASK_ENV=development python -m flask run

run:
	cd truncat && FLASK_APP=app FLASK_ENV=production python -m flask run
