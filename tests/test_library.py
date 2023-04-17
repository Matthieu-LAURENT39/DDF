import datedataformat
from datetime import date


def test_parse():
    test_input = """First line of header
  Second line of header  
Third line of header


[17/04/2023]
First line
Second line
Third line

[18/04/2023]
Fourth line
Fifth line
Sixth line
"""

    output = datedataformat.parse(test_input)
    assert (
        output.file_header
        == """First line of header
  Second line of header  
Third line of header"""
    )

    assert (
        output.raw_file_header
        == """First line of header
  Second line of header  
Third line of header

"""
    )

    assert output.day(date(2023, 4, 18)) == ["Fourth line", "Fifth line", "Sixth line"]
    assert output.data == {
        date(2023, 4, 17): ["First line", "Second line", "Third line"],
        date(2023, 4, 18): ["Fourth line", "Fifth line", "Sixth line"],
    }


def test_render():
    test_input = datedataformat.DDF(
        file_header="Hello\nWorld!",
        _file_header_newlines=1,
        data={
            date(2023, 4, 17): ["line1", "line2"],
            date(2023, 4, 18): ["line3", "line4"],
        },
    )

    output = datedataformat.render(test_input)
    assert (
        output
        == """Hello
World!

[17/04/2023]
line1
line2

[18/04/2023]
line3
line4
"""
    )


def test_round_trip():
    test_input = """First line of header
  Second line of header  
Third line of header
[17/04/2023]
First line
Second line
Third line
[18/04/2023]
Fourth line
Fifth line
Sixth line
"""

    assert test_input == datedataformat.render(datedataformat.parse(test_input))
