import pytest

from collections import Counter


@pytest.fixture
def color_counts():
    return [
        Counter(["a", "b", "c"]),
        Counter(["a"]),
        Counter(["a", "a", "a", "b", "b", "c"]),
    ]


def test_round_1_solver(color_counts):
    for j, color_count in enumerate(color_counts):
        try:
            color1, color2 = color_count.most_common(2)
            assert color1[0] == "a"
            assert color2[0] == "b"

        except ValueError:
            color1 = color_count.most_common(1)[0][0]
            assert "a" == color1
