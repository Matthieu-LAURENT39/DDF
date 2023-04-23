# -*- coding: utf-8 -*-
# @Author: Mattlau04
# @Date:   2023-04-23 18:28:18
# @Last Modified by:   Mattlau04
# @Last Modified time: 2023-04-23 18:28:42

from .ddf import DDF, parse
import click
from .exceptions import DDFParseError


def _parse_file(text: str, strict: bool) -> DDF:
    try:
        return parse(text, strict=strict)
    except DDFParseError as e:
        raise click.ClickException(str(e))
