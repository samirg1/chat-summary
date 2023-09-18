import subprocess
import sys


def send_message(chat_name: str, message: str) -> None:
    if message == "":
        print("empty message, no message sent", file=sys.stderr)
        exit(1)

    # TESTING
    print(f"{chat_name = }")
    chat_name = "Test"

    try:
        subprocess.check_call(["osascript", "-e", f'tell application "Messages"\nsend "{message}" to chat "{chat_name}"\n end tell'])
    except subprocess.CalledProcessError:
        print(f"unable to send message to group chat", file=sys.stderr)
        exit(0)

    print("message sent successfully!")
