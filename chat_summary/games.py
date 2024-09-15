import datetime
import re


from chat_summary.game import RESULT, Game


class Wordle(Game):
    def get_display_emojis(self) -> str:
        return "🟨⬛🟩"

    def get_score_title(self) -> str:
        return "GUESSES"

    def _get_regex(self) -> str:
        return r"^Wordle (\d{1,3}(?:,\d{3})*|\d{1,4}) (1|2|3|4|5|6|X)/6"

    def analyse_message(self, message: str) -> RESULT | None:
        matches = re.match(self._regex, message)
        if matches is None:
            return None

        number = int(matches[1].replace(",", ""))
        self._update_range(number)

        if matches[2] == "X":
            return RESULT(number, False)
        guesses = int(matches[2])

        return RESULT(number, True, guesses)


class Connections(Game):
    def get_display_emojis(self) -> str:
        return "🟪🟦🟩"

    def get_score_title(self) -> str:
        return "GUESSES"

    def _get_regex(self) -> str:
        return r"^Connections \nPuzzle #(\d{1,4})"

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
    def get_display_emojis(self) -> str:
        return "⬛🟪🟩"

    def get_score_title(self) -> str:
        return "GUESSES"

    def _get_regex(self) -> str:
        return r"^nerdlegame (\d{1,4}) (1|2|3|4|5|6|X)/6"

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


class Strands(Game):
    def get_display_emojis(self) -> str:
        return "🟡💡🔵"

    def get_score_title(self) -> str:
        return "HINTS USED"

    def _get_regex(self) -> str:
        return r"^Strands #(\d{1,4})"

    def analyse_message(self, message: str) -> RESULT | None:
        matches = re.match(self._regex, message)
        if matches is None:
            return None

        number = int(matches[1])
        self._update_range(number)

        score = message.count("💡")

        return RESULT(number, True, score)


class Mini(Game):
    def get_display_emojis(self) -> str:
        return "⬜️🔷⬛️"

    def get_score_title(self) -> str:
        return "TIME (S)"

    def _get_regex(self) -> str:
        return r"^https://www.nytimes.com/badges/games/mini.html\?d=(\d{4}-\d{2}-\d{2})&t=(\d{1,5})|^I solved the (\d{1,2}/\d{1,2}/\d{4}) New York Times Mini Crossword in (\d{1,2}:\d{1,2})!"

    def _days_since_last(self, date: datetime.datetime) -> int:
        return (datetime.datetime.now() - date).days

    def analyse_message(self, message: str) -> RESULT | None:
        matches = re.match(self._regex, message)
        if matches is None:
            return None

        if matches[3] is not None:
            mins, secs = matches[4].split(":")
            time_taken = int(mins) * 60 + int(secs)
            raw_date = matches[3]
            if raw_date[1] == "/":
                raw_date = "0" + raw_date
            date = datetime.datetime.strptime(raw_date, "%m/%d/%Y")
        else:
            time_taken = int(matches[2])
            date = datetime.datetime.strptime(matches[1], "%Y-%m-%d")

        days_since_last = self._days_since_last(date)
        self._update_range(days_since_last)

        return RESULT(days_since_last, True, time_taken)


class Betweenle(Game):
    def get_display_emojis(self) -> str:
        return "🟩🏆⬜"

    def get_score_title(self) -> str:
        return "TROPHIES LOST"

    def _get_regex(self) -> str:
        return r"^Betweenle (\d{1,4}) - (1|2|3|4|5|X)/5"

    def analyse_message(self, message: str) -> RESULT | None:
        matches = re.match(self._regex, message)
        if matches is None:
            return None

        number = int(matches[1])
        self._update_range(number)

        if matches[2] == "X":
            return RESULT(number, False)
        trophies_lost = 5 - int(matches[2])

        return RESULT(number, True, trophies_lost)
