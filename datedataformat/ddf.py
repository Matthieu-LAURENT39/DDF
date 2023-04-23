from datetime import date, datetime
from dataclasses import dataclass, field
from collections import defaultdict
from io import StringIO
from .exceptions import DDFParseError


@dataclass
class DDF:
    file_header: str
    data: dict[date, list[str]]

    _file_header_blank_lines: int = 2
    """
    How many blank lines are present after the file header
    In strict parsing, this should be 2.
    """
    _data_blank_lines: dict[date, int] = field(default_factory=dict)
    """
    How many blank lines are present after a date's data lines
    In strict parsing, this should be 1.
    """

    def day(self, date: date) -> list[str] | None:
        return self.data.get(date)

    @property
    def raw_file_header(self) -> str:
        return self.file_header + self._file_header_blank_lines * "\n"


def parse(text: str, *, strict: bool = False) -> DDF:
    raw_file_header = StringIO()
    data = defaultdict(list)
    _data_blank_lines = defaultdict(lambda: 0)
    current_date = None

    def _count_empty_lines(current_date) -> None:
        # Get how many empty lines there were after the last data line
        for l in reversed(data[current_date]):
            if l:
                break
            _data_blank_lines[current_date] += 1
        # We need to check if it's not 0, otherwise
        # it would delete all data for that day
        if _data_blank_lines[current_date] > 0:
            data[current_date] = data[current_date][: -_data_blank_lines[current_date]]

    for line_nbr, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()

        # If the line is a date header, update current_date
        if line.startswith("[") and line.endswith("]"):
            if current_date is not None:
                if (not data[current_date]) and strict:
                    raise DDFParseError(
                        f"No data lines for date [{current_date:%d/%m/%Y}] (line {line_nbr-1})"
                    )
                _count_empty_lines(current_date)
                if strict and (_data_blank_lines[current_date] != 1):
                    raise DDFParseError(
                        f"Invalid amount of blank lines after last data line for date [{current_date:%d/%m/%Y}] (Is {_data_blank_lines[current_date]}, should be 1)"
                    )

            current_date = datetime.strptime(line, "[%d/%m/%Y]").date()
            continue

        # Otherwise, append the line to the current date's data
        # or the file header if there wasn't any date header yet
        elif current_date is None:
            raw_file_header.write(f"{raw_line}\n")
        else:
            if (not data[current_date]) and (not line) and strict:
                # If there is a blank line between the date header
                # and the first data line
                raise DDFParseError(
                    f"Empty line between date header and first data line (line {line_nbr})"
                )
            if line:
                if (data[current_date]) and (not data[current_date][-1]) and (strict):
                    # We got a data line but there was a blank line between that one
                    # and the previous one
                    raise DDFParseError(
                        f"Empty line between 2 data lines (line {line_nbr-1})"
                    )

            data[current_date].append(line)

    # Count empty lines for the last date
    if current_date:
        _count_empty_lines(current_date)
        # splitlines() doesn't let us know if we had a single newline at the end, so
        # we need a workaround
        if strict and (text.rstrip("\n") + "\n" != text):
            raise DDFParseError(f"File should end with a single newline.")

    raw_file_header = raw_file_header.getvalue()
    file_header = raw_file_header.rstrip("\n")
    _file_header_blank_lines = max(len(raw_file_header) - len(file_header) - 1, 0)

    if file_header:
        if strict and _file_header_blank_lines != 2:
            raise DDFParseError(
                "Invalid amount of blank lines after file header (should be 2)"
            )

    return DDF(
        file_header=file_header,
        _file_header_blank_lines=_file_header_blank_lines,
        _data_blank_lines=_data_blank_lines,
        data=dict(data),
    )


def render(ddf: DDF) -> str:
    output = StringIO()
    output.write(ddf.raw_file_header)
    # Don't add a newline at the start if header was empty
    if ddf.raw_file_header:
        output.write("\n")

    for i, (date, values) in enumerate(ddf.data.items(), start=1):
        output.write(f"[{date:%d/%m/%Y}]\n")
        output.writelines(f"{v}\n" for v in values)
        output.write("\n" * ddf._data_blank_lines.get(date, 0))

    return output.getvalue()
