import io
from math import inf
import sys
from typing import Iterable, NamedTuple

from chat_summary.game import Game, GameScore


class MESSAGE(NamedTuple):
    content: str
    phone_number: str


class ChatMember:
    def __init__(self, name: str, number: str):
        self.name = name
        self.number = number
        self.game_scores: dict[str, GameScore] = {}

    def __repr__(self) -> str:
        return f"({self.name}, {self.number})"


class ChatSummary:
    def __init__(self, members: list[ChatMember], games: tuple[Game, ...]) -> None:
        self._members = members
        self._games = games

        for member in self._members:
            for game in games:
                name = type(game).__name__
                member.game_scores[name] = GameScore()

    def populate(self, messages: Iterable[MESSAGE]) -> None:
        for content, phone_number in messages:
            phone_number = phone_number or ""
            member = next((member for member in self._members if member.number == phone_number), None)
            if not member or not content:
                continue

            for game in self._games:
                result = game.analyse_message(content)
                if result is None:
                    continue
                member.game_scores[type(game).__name__].add(result)

    def get_display(self) -> str:
        out = io.StringIO()
        for i, game in enumerate(self._games):
            game_name = type(game).__name__
            total_days = game.range
            if total_days == 0:
                print(f"🟥 no '{game_name}' messages found 🟥", file=sys.stderr)
                continue

            out.write(f"\n🟨🟨🟨 {game_name.upper()} 🟨🟨🟨\n\n")

            max_name_length = len(max(self._members, key=lambda user: len(user.name)).name)  # get the length of the longest name

            self._members.sort(key=lambda member: member.game_scores[game_name].completed, reverse=True)
            out.write(f"COMPLETIONS ({total_days} days)\n")
            for j, member in enumerate(self._members, start=1):
                game_score = member.game_scores[game_name]
                if game_score.completed == 0:
                    continue
                out.write(f"{j}. {member.name:.<{max_name_length}}..{game_score.completed}/{game_score.attempts}\n")

            self._members.sort(key=lambda member: inf if member.game_scores[game_name].average_guesses == 0 else member.game_scores[game_name].average_guesses)
            out.write("\nAVERAGE GUESSES\n")
            for k, member in enumerate(self._members, start=1):
                game_score = member.game_scores[game_name]
                if game_score.average_guesses == 0:
                    continue
                out.write(f"{k}. {member.name:.<{max_name_length}}..{game_score.average_guesses:.2f}\n")

            if i != len(self._games) - 1:
                out.write("\n")

        return out.getvalue()
