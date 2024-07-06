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

revision:  ##@ApplicationDev Generate migrations
	cd ./app/database && alembic revision --autogenerate

migrate:  ##@ApplicationDev Generate migrations
	cd ./app/database && alembic upgrade $(args)

linters:  ##@Linters Run linters
	isort . --settings-file=./setup.cfg
	flake8 . --config=./setup.cfg

run:  ##@ApplicationDev Run django
	make migrate head && python -m app

%::
	echo $(MESSAGE)
