from invoke import Exit, UnexpectedExit, task

from . import common, docker

DEFAULT_FOLDERS = "."


@task
def isort(
    context,
    path=DEFAULT_FOLDERS,
    params="--settings-file=./setup.cfg",
    service="bot",
):
    """Command to fix imports formatting."""
    common.success("Linters: ISort running")
    docker.docker_compose_run(
        context,
        service,
        command=f"isort {path} {params}",
    )


@task
def flake8(
    context,
    path=DEFAULT_FOLDERS,
    params="--config=./setup.cfg",
    service="bot",
):
    """Run `flake8` linter."""
    common.success("Linters: Flake8 running")
    docker.docker_compose_run(
        context,
        service,
        command=f"flake8 {path} {params}",
    )


@task
def all(context, path=DEFAULT_FOLDERS):
    """Run all linters."""
    common.success("Linters: Running all linters")
    linters = (isort, flake8)
    failed = []
    for linter in linters:
        try:
            linter(context, path)
        except UnexpectedExit:
            failed.append(linter.__name__)
    if failed:
        common.error(
            f"Linters failed: {', '.join(map(str.capitalize, failed))}",
        )
        raise Exit(code=1)
