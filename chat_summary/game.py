import re
from abc import ABC, abstractmethod
from typing import Literal, NamedTuple


class RESULT(NamedTuple):
    game_number: int
    completed: bool
    guesses: int = -1


class Game(ABC):
    _BIG_INTEGER = 1_000_000

    def __init__(self) -> None:
        self._min = self._BIG_INTEGER
        self._max = 0
        self._regex = re.compile(self._get_regex())
        super().__init__()

    @abstractmethod
    def _get_regex(self) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def analyse_message(self, message: str) -> None | RESULT:
        pass  # pragma: no cover

    @property
    def range(self) -> int:
        return 0 if self._min == self._BIG_INTEGER else self._max - self._min

    def _update_range(self, game_number: int) -> None:
        self._min = min(self._min, game_number)
        self._max = max(self._max, game_number)


class GameScore:
    def __init__(self) -> None:
        self._games: set[int] = set()
        self._fails: set[int] = set()
        self._total_guesses = 0

    def add(self, _result: RESULT) -> None:
        if _result.completed:
            self._games.add(_result.game_number)
            self._total_guesses += _result.guesses
        else:
            self._fails.add(_result.game_number)

    @property
    def completed(self) -> int:
        return len(self._games)

    @property
    def attempts(self) -> int:
        return self.completed + len(self._fails)

    @property
    def average_guesses(self) -> float | Literal[0]:
        return 0 if len(self._games) == 0 else self._total_guesses / len(self._games)
