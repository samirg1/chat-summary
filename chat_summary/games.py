import re

from chat_summary.game import RESULT, Game


class Wordle(Game):
    def _get_regex(self) -> str:
        return r"Wordle (\d{1,4}) (1|2|3|4|5|6|X)/6"

    def analyse_message(self, message: str) -> RESULT | None:
        matches = re.match(self._regex, message)
        if matches is None:
            return None

        number = int(matches[1])
        self._update_range(number)

        if matches[2] == "X":
            return RESULT(number, False)
        guesses = int(matches[2])

        return RESULT(number, True, guesses)


class Connections(Game):
    def _get_regex(self) -> str:
        return r"Connections \nPuzzle #(\d{1,4})"

    def analyse_message(self, message: str) -> RESULT | None:
        matches = re.match(self._regex, message)
        if matches is None:
            return None

        number = int(matches[1])
        self._update_range(number)

        lines = message.split("\n")
        try:
            last_line, i = next((line, i) for i, line in enumerate(reversed(lines)) if line and line[0] in ("🟪", "🟦", "🟩", "🟨"))
        except StopIteration:
            return None

        if all(square == last_line[0] for square in last_line):
            return RESULT(number, True, len(lines) - 2 - i)

        return RESULT(number, False)


class Nerdle(Game):
    def _get_regex(self) -> str:
        return r"nerdlegame (\d{1,4}) (1|2|3|4|5|6|X)/6"

    def analyse_message(self, message: str) -> RESULT | None:
        matches = re.match(self._regex, message)
        if matches is None:
            return None

        number = int(matches[1])
        self._update_range(number)

        if matches[2] == "X":
            return RESULT(number, False)
        guesses = int(matches[2])

        return RESULT(number, True, guesses)
