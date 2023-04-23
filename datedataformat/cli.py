# -*- coding: utf-8 -*-
# @Author: Mattlau04
# @Date:   2023-04-22 19:16:39
# @Last Modified by:   Mattlau04
# @Last Modified time: 2023-04-23 18:24:09
import click
import datetime
from ._cli_utils import _parse_file
from .ddf import render, parse
from .exceptions import DDFParseError


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("file", type=click.File("r+"))
@click.argument("data", type=str)
@click.option(
    "--date",
    type=click.DateTime(),
    default=datetime.date.today().strftime("%Y-%m-%d"),
    help="The date to add the record to (defaults to today, format: YYYY-MM-DD).",
)
def add(file: click.File, data: str, date: datetime.datetime):
    date = date.date()
    ddf_data = _parse_file(file.read(), strict=False)
    if ddf_data.data.get(date) is None:
        ddf_data.data[date] = []
    ddf_data.data[date].append(data)
    file.seek(0)
    file.write(render(ddf_data))
    file.truncate()


@cli.command()
@click.argument("file", type=click.File("r"))
@click.option("--strict", is_flag=True, help="Enable strict validation")
def validate(file: click.File, strict: bool):
    try:
        parse(file.read(), strict=strict)
    except DDFParseError as e:
        click.echo(str(e), err=True)
        return

    click.echo("File is valid!")
