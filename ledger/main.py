import click

@click.group()


def cli() -> None:
    print("Hello world")
