from invoke import task

from . import common, docker, git


@task
def install_tools(context):
    """Install cli dependencies, and tools needed to install requirements."""
    context.run("pip install setuptools pip pip-tools wheel poetry")


@task
def install_requirements(context):
    """Install local development requirements."""
    common.success("Install requirements with poetry")
    context.run("poetry install")


@task
def lock_requirements(context):
    """Lock requirements."""
    context.run("poetry lock --no-update")


@task
def migrations(context, command="init migrations"):
    """Run alembic migrations."""
    docker.run_container(context, command=f"alembic {command}")


@task
def init(context):
    """Prepare env for working with project."""
    common.success("Setting up git config")
    git.hooks(context)
    git.gitmessage(context)
    common.success("Initial assembly of all dependencies")
    install_tools(context)
    install_requirements(context)
    docker.build(context)
    lock_requirements(context)
    migrations(context)
