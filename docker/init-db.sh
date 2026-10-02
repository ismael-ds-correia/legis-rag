#!/bin/bash
set -e

function create_user_and_database() {
	local database=$1
	echo "  Creating database '$database'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
	    CREATE DATABASE $database;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
	echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
	for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
		create_user_and_database $db
	done
	echo "Multiple databases created"
fi

if [ -f /docker-entrypoint-initdb.d/schema.sql ]; then
    echo "Aplicando schema.sql no banco 'camara_db'..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "camara_db" -f /docker-entrypoint-initdb.d/schema.sql
    echo "Schema aplicado com sucesso!"
fi