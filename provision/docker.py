from invoke import task

CONTAINERS = {
    "dev": "docker-compose",
    "prod": "docker-compose -f docker-compose.prod.yml",
}


@task
def build(context, compose="dev"):
    """Build project."""
    return context.run(
        f"{CONTAINERS[compose]} build",
    )


@task
def run(context, compose="dev"):
    """Run postgres, redis, telegram app."""
    return context.run(
        f"{CONTAINERS[compose]} up",
    )


@task
def run_build(context, compose="dev"):
    """Run and build app."""
    return context.run(
        f"{CONTAINERS[compose]} up --build",
    )


@task
def clean_volumes(context, compose="dev"):
    """Clean volumes."""
    return context.run(f"{CONTAINERS[compose]} down -v")


@task
def run_container(context, command="", compose="dev"):
    """Base template for commands with django container."""
    return context.run(f"{CONTAINERS[compose]} run --rm bot {command}")


@task
def delcont(context):
    """Delete all docker containers."""
    return context.run("docker rm -f $(docker ps -a -q)")
