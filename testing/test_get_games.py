import pytest
from chat_summary.game import Game
from chat_summary.get_available_games import get_available_chat_games


@pytest.mark.parametrize(("name", "game"), list(get_available_chat_games()))
def test_chat_games(name: str, game: Game):
    assert type(game).__name__ == name
    assert isinstance(game, Game) and type(game) != Game