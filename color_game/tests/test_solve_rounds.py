import pytest

from collections import Counter


@pytest.fixture
def color_counts_list():
    return [
        Counter(["a", "b", "c"]),
        Counter(["a", "a"]),
        Counter(["a", "a", "a","a", "a", "a", "b", "b"]),
        Counter(["a", "a", "a", "b", "b", "c"]),
    ]


def test_two_most_chosen_win(color_counts_list):
    for j, color_counts in enumerate(color_counts_list):
        if len(color_counts) == 1:
            color1, count = color_counts.popitem()
            amount_players = count
            amount_of_winners = max(1, int(0.25 * amount_players))
            assert amount_of_winners == 1

        elif len(color_counts) == 2:
            color1, color2 = color_counts.most_common(2)
            amount_players = color1[1] + color2[1]
            amount_of_winners = max(1, int(0.25 * amount_players))
            assert amount_of_winners == 2
        else:
            color1, color2 = color_counts.most_common(2)
            amount_of_winners = color1[1] + color2[1]
            if j == 0:
                assert amount_of_winners == 2
            else:
                assert amount_of_winners == 5



