import click
from ledger.crud import create

@click.group()


def cli() -> None:
    print("Hello world")


cli.add_command(create)