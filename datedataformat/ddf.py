from datetime import date, datetime
from dataclasses import dataclass
from collections import defaultdict
from io import StringIO


@dataclass
class DDF:
    file_header: str
    data: dict[date, list[str]]

    _file_header_newlines: int = 2
    """
    How many blank lines are present after the file header
    In strict parsing, this should be 2.
    """

    def day(self, date: date) -> list[str] | None:
        return self.data.get(date)

    @property
    def raw_file_header(self) -> str:
        return self.file_header + self._file_header_newlines * "\n"


def parse(text: str) -> DDF:
    raw_file_header = StringIO()
    data = defaultdict(list)
    current_date = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # If the line is a date header, update current_date
        if line.startswith("[") and line.endswith("]"):
            current_date = datetime.strptime(line, "[%d/%m/%Y]").date()
            continue

        # Otherwise, append the line to the current date's data
        # or the file header if there wasn't any date header yet
        elif current_date is None:
            raw_file_header.write(f"{raw_line}\n")
        else:
            # Don't add empty line
            if line:
                data[current_date].append(line)

    raw_file_header = raw_file_header.getvalue()
    file_header = raw_file_header.rstrip("\n")
    file_header_newlines = len(raw_file_header) - len(file_header) - 1
    return DDF(
        file_header=file_header,
        _file_header_newlines=file_header_newlines,
        data=dict(data),
    )


def render(ddf: DDF) -> str:
    output = StringIO()
    output.write(ddf.raw_file_header)

    for date, values in ddf.data.items():
        output.write(f"\n[{date:%d/%m/%Y}]\n")
        output.writelines(f"{v}\n" for v in values)

    return output.getvalue()
