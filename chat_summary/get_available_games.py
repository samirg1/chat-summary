from typing import Generator

import chat_summary.games as chat_games
from chat_summary.game import Game


def get_available_chat_games() -> Generator[tuple[str, Game], None, None]:
    for name in dir(chat_games):
        module = eval(f"chat_games.{name}")
        if not isinstance(module, type):
            continue

        try:
            obj = module()
        except TypeError:
            continue

        if isinstance(obj, Game) and type(obj) != Game:
            yield name, obj
