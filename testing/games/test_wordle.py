import pytest

from chat_summary.games import Wordle


@pytest.fixture
def wordle_game():
    return Wordle()


@pytest.mark.parametrize("number", (1, 10, 30, 200, 800, 1000))
def test_valid_message_no_guesses(number: int, wordle_game: Wordle):
    message = f"Wordle {number} X/6"
    result = wordle_game.analyse_message(message)
    assert result == (number, False, -1)


@pytest.mark.parametrize("guesses", (1, 2, 3, 4, 5, 6))
def test_valid_message_with_guesses(guesses: int, wordle_game: Wordle):
    message = f"Wordle 456 {guesses}/6"
    result = wordle_game.analyse_message(message)
    assert result == (456, True, guesses)


@pytest.mark.parametrize(
    "message",
    (
        "Wordle ahhaahahahaha",
        "Wordle 12a X/6",
        "Wordle 789 7/6",
        "Wordle 789 0/6",
        "WordlE 789 2/6",
        "WordlE 789 2/6",
        "Wordle 7 2/4",
    ),
)
def test_invalid_message(message: str, wordle_game: Wordle):
    result = wordle_game.analyse_message(message)
    assert result is None


if __name__ == "__main__":
    pytest.main()
