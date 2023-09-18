import argparse
from typing import Sequence

import chat_summary.messages as chat_summary_messages
from chat_summary.chat import ChatSummary
from chat_summary.game import Game
from chat_summary.get_available_games import get_available_chat_games
from chat_summary.send_message import send_message


def main(argv: Sequence[str] | None = None) -> int:
    argparser = argparse.ArgumentParser()
    argparser.add_argument("user", help="user's login name")
    argparser.add_argument("chat_name", help="name of chat to get summary of")
    argparser.add_argument("--silence-contacts", action="store_true", help="silence the 'unable to find contacts' error")
    argparser.add_argument("--send-message", action="store_true", help="send results back to group chat")
    for name, game in get_available_chat_games():
        argparser.add_argument(f"-{name[0]}", f"--{name}", dest="games", action="append_const", const=game)

    args = argparser.parse_args(argv)

    games: list[Game] = list(set(args.games or []))
    games.sort(key=lambda cls: type(cls).__name__)

    messages_connection = chat_summary_messages.MessagesDB(args.user, args.chat_name, args.silence_contacts)
    messages, members = messages_connection.get_messages_members_from_chat()

    chat_summary = ChatSummary(members, tuple(games))
    chat_summary.populate(messages)
    summary = chat_summary.get_display()

    if args.send_message:
        if input("are you sure you want to send the message? (Y): ") == "Y":
            send_message(args.chat_name, summary)
    else:
        print(summary)

    return 0


if __name__ == "__main__":
    exit(main())  # pragma: no cover
