ifeq ($(shell test -e '.env' && echo -n yes),yes)
	include .env
endif

args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

# Commands
help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

docker-up-build:  ##@Application Run and build application server
	docker-compose up --build --remove-orphans

docker-up-buildd:  ##@Application Run and build application server in daemon
	docker-compose up -d --build --remove-orphans

docker-up:  ##@Application Run application server
	docker-compose up

docker-upd:  ##@Application Run application server in daemon
	docker-compose up -d

docker-down:  ##@Application Stop application in docker
	docker-compose down --remove-orphans

docker-downv:  ##@Application Stop application in docker and remove volumes
	docker-compose down -v --remove-orphans

docker-bot-run:  ##@Application Run bot container with command
	docker-compose run --rm bot $(args)

linters:  ##@Linters Run linters
	make docker-bot-run "make linters"

migrate:  ##@Application Apply migrations
	make docker-bot-run "make migrate"

open-db:  ##@Database Open database inside docker-image
	docker exec -it postgres psql -d $(POSTGRES_DB) -U $(POSTGRES_USER) -p $(POSTGRES_PORT)

docker-login:  ##@Docker Login in GitHub Container Registry
	echo $(PAT) | docker login ghcr.io -u $(USERNAME) --password-stdin

docker-clean:  ##@Docker Remove all unused docker objects
	docker system prune --all -f

docker-cleanv:  ##@Docker Remove all docker objects with volumes
	docker system prune --all --volumes -f

docker-pull-prod:  ##@Docker Pulling containers
	docker-compose -f docker-compose.prod.yml pull

docker-stop:  ##@Docker Stop all docker containers
	@docker rm -f $$(docker ps -aq) || true

%::
	echo $(MESSAGE)
