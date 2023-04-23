import datedataformat
import pytest
from datetime import date


def test_strict_valid():
    valid_input = """Wow, this is
such a cool file header
i really like it


[23/04/2023]
my data
"""
    datedataformat.parse(valid_input, strict=True)


# The file header should be separated by 2 blank lines from the first header
@pytest.mark.parametrize(
    "invalid_input",
    [
        """huh, this is
not such a cool file header
i don't like it

[23/04/2023]
my data
""",
        """huh, this header
really sucks
i don't like it at all!



[23/04/2023]
my data
""",
    ],
)
def test_strict_file_header(invalid_input: str):
    with pytest.raises(datedataformat.DDFParseError) as e:
        datedataformat.parse(invalid_input, strict=True)
    assert "Invalid amount of blank lines after file header (should be 2)" == str(
        e.value
    )


# There should be no blank line between the date header and the first data line
@pytest.mark.parametrize(
    "invalid_input",
    [
        """huh, this is
not such a cool file header
i don't like it


[23/04/2023]

my data
""",
        """huh, this header
really sucks
i don't like it at all!


[23/04/2023]


my data""",
    ],
)
def test_date_header_data_spacing(invalid_input: str):
    with pytest.raises(datedataformat.DDFParseError) as e:
        datedataformat.parse(invalid_input, strict=True)
    assert "Empty line between date header and first data line" in str(e.value)


# Each data line should be separated by a single newline
def test_data_lines_spacing():
    invalid_input_1 = """[23/04/2023]
my data 1
my data 2


my data 3
"""
    invalid_input_2 = """[23/04/2023]
        
my data 1
my data 2
my data 3
"""

    with pytest.raises(datedataformat.DDFParseError) as e:
        datedataformat.parse(invalid_input_1, strict=True)
    assert "Empty line between 2 data lines (line 5)" == str(e.value)

    with pytest.raises(datedataformat.DDFParseError) as e:
        datedataformat.parse(invalid_input_2, strict=True)
    assert "Empty line between date header and first data line (line 2)" == str(e.value)


# There should be a single blank line between the last data line and the next header
@pytest.mark.parametrize(
    "invalid_input",
    [
        """huh, this is
not such a cool file header
i don't like it


[23/04/2023]
my data
[24/04/2023]
my other data
""",
        """huh, this header
really sucks
i don't like it at all!


[23/04/2023]
my data


[24/04/2023]
my other data
""",
    ],
)
def test_date_blocks_spacing(invalid_input: str):
    with pytest.raises(datedataformat.DDFParseError) as e:
        datedataformat.parse(invalid_input, strict=True)
    assert "Invalid amount of blank lines after last data line for date" in str(e.value)


# Dates without entry should not be present in the file
@pytest.mark.parametrize(
    "invalid_input",
    [
        """huh, this is
not such a cool file header
i don't like it


[23/04/2023]
[24/04/2023]
my other data
""",
        """[23/04/2023]
my data

[24/04/2023]
my other data

[25/04/2023]
[26/04/2023]
even more data
""",
    ],
)
def test_empty_blocks(invalid_input: str):
    with pytest.raises(datedataformat.DDFParseError) as e:
        datedataformat.parse(invalid_input, strict=True)
    # This tends to also raise "Empty line between date header and first data line"
    assert "No data lines for date" in str(e.value)


# The file should end with a single newline
@pytest.mark.parametrize(
    "invalid_input",
    [
        """huh, this is
not such a cool file header
i don't like it


[23/04/2023]
my data

[24/04/2023]
my other data

""",
        """[23/04/2023]
my data

[24/04/2023]
my other data

[25/04/2023]
even more data""",
    ],
)
def test_newline_end_of_file(invalid_input: str):
    with pytest.raises(datedataformat.DDFParseError) as e:
        datedataformat.parse(invalid_input, strict=True)
    assert "File should end with a single newline." in str(e.value)
