from invoke import Collection

from provision import (
    docker,
    git,
    linters,
    project,
)

ns = Collection(
    docker,
    linters,
    project,
    git,
)

# Configurations for run command
ns.configure(
    dict(
        run=dict(
            pty=True,
            echo=True,
        ),
    ),
)
