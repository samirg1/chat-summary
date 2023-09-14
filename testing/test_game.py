import pytest

from chat_summary.game import RESULT, GameScore
from chat_summary.games import Wordle


@pytest.fixture
def game_score():
    return GameScore()


def test_initial_state(game_score: GameScore):
    assert game_score.completed == 0
    assert game_score.attempts == 0
    assert game_score.average_guesses == 0


def test_add_completed_game(game_score: GameScore):
    result = RESULT(game_number=1, completed=True, guesses=4)
    game_score.add(result)
    assert game_score.completed == 1
    assert game_score.attempts == 1
    assert game_score.average_guesses == 4.0


def test_add_failed_game(game_score: GameScore):
    result = RESULT(game_number=2, completed=False)
    game_score.add(result)
    assert game_score.completed == 0
    assert game_score.attempts == 1
    assert game_score.average_guesses == 0


def test_add_multiple_games(game_score: GameScore):
    result1 = RESULT(game_number=1, completed=True, guesses=4)
    result2 = RESULT(game_number=2, completed=True, guesses=3)
    result3 = RESULT(game_number=3, completed=False)
    game_score.add(result1)
    game_score.add(result2)
    game_score.add(result3)
    assert game_score.completed == 2
    assert game_score.attempts == 3
    assert game_score.average_guesses == 3.5


def test_average_guesses_with_no_completed_games(game_score: GameScore):
    result = RESULT(game_number=1, completed=False)
    game_score.add(result)
    assert game_score.average_guesses == 0


def test_game():
    game = Wordle()
    assert game.range == 0
    assert game.analyse_message("Wordle 314 4/6")
    assert game.range == 0
    assert game.analyse_message("Wordle 316 4/6")
    assert game.range == 2