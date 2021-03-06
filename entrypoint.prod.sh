#!/bin/sh

if [ "$DATABASE" = 'postgres' ]
then 
    echo "[*] Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done

    echo "[OK] Postgres Started Successfully..."
fi

python manage.py migrate
python manage.py initadmin
python manage.py collectstatic --no-input

exec "$@"