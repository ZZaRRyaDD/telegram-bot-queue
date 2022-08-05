from invoke import task

START_COMMAND_DEV = "docker-compose"
START_COMMAND_PROD = "docker-compose -f docker-compose.prod.yml"


@task
def build(context, dev=True):
    """Build project."""
    return context.run(
        f"{START_COMMAND_DEV if dev else START_COMMAND_PROD} build",
    )


@task
def run(context, dev=True):
    """Run postgres, redis, telegram app."""
    return context.run(
        f"{START_COMMAND_DEV if dev else START_COMMAND_PROD} up",
    )


@task
def run_build(context, dev=True):
    """Run and build app."""
    return context.run(
        f"{START_COMMAND_DEV if dev else START_COMMAND_PROD} up --build",
    )


@task
def clean_volumes(context):
    """Clean volumes."""
    return context.run(f"{START_COMMAND_DEV} down -v")


@task
def run_container(context, command=""):
    """Base template for commands with django container."""
    return context.run(f"{START_COMMAND_DEV} run --rm bot {command}")


@task
def delcont(context):
    """Delete all docker containers."""
    return context.run("docker rm -f $(docker ps -a -q)")
