#! /usr/bin/env pipenv run -- python3
import click


@click.command()
@click.option('--version', '-v', flag_value=True, help="Show Viper version")
@click.argument('args', nargs=-1)
def app(version, args):
    if version:
        click.echo('Viper 0.0.1')

    elif args:
        click.echo(f"I know I'm supposed to compile '{args[0]}', but I wont 😜")
        click.echo(f"arguments = [{', '.join(args)}]")

    else:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()


if __name__ == "__main__":
    app()
