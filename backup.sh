source .env

docker-compose exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB -f ./dumps/dump.sql
