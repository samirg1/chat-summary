import argparse
from typing import Sequence

from chat_summary.chat import ChatSummary
from chat_summary.game import Game
from chat_summary.get_available_games import get_available_chat_games
from chat_summary.messages import MessagesDB
from chat_summary.update_readme import update_readme  # type: ignore


def main(argv: Sequence[str] | None = None) -> int:
    argparser = argparse.ArgumentParser()
    argparser.add_argument("user", help="user's login name")
    argparser.add_argument("chat_name", help="name of chat to get summary of")
    argparser.add_argument("--silence-contacts", action="store_true", help="silence the 'unable to find contacts' error")

    games: list[Game] = []
    for name, game in get_available_chat_games():
        games.append(game)
        argparser.add_argument(f"-{name[0]}", f"--{name}", dest="games", action="append_const", const=game)
    games.sort(key=lambda cls: type(cls).__name__)

    args = argparser.parse_args(argv)

    messages_connection = MessagesDB(args.user, args.chat_name, args.silence_contacts)
    messages, members = messages_connection.get_messages_members_from_chat()

    chat_summary = ChatSummary(members, tuple(games))
    chat_summary.populate(messages)
    chat_summary.display()

    return 0


if __name__ == "__main__":
    exit(main())
