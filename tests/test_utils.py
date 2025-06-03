import pytest
from climate_game.utils import get_round


@pytest.mark.parametrize(
    "file_name",
    [("2025_05_16_14_16_round_2.jsonl", 2), ("18.jsonl", 18)],
)
def test_get_round(file_name: tuple) -> None:
    name_file, r = file_name
    result = get_round(name_file)
    assert isinstance(result, int)
    assert result == r
