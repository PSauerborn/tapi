import logging

import typer
from rich import print

from tapi.cli.run import run_command


LOGGER = logging.getLogger("tapi.cli")

CLI = typer.Typer()
# add command to run application
CLI.command("run")(run_command)


def unsupported():
    print("[bold red]ERROR:[/bold red] This functionality is not yet supported.")
    raise typer.Exit()


CLI.command("package")(unsupported)
CLI.command("deploy")(unsupported)
