from invoke import task

START_COMMAND = "docker-compose -f bot.yml"


@task
def build(context):
    """Build project."""
    return context.run(f"{START_COMMAND} build")


@task
def run(context):
    """Run postgres, redis, django."""
    return context.run(f"{START_COMMAND} up")


@task
def runbuild(context):
    """Run postgres, redis, django."""
    return context.run(f"{START_COMMAND} up --build")


@task
def delcont(context):
    """Delete all docker containers."""
    return context.run("docker rm -f $(docker ps -a -q)")
