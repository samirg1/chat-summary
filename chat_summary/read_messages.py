import sqlite3


def read_messages(db_location: str, chat_id: str, self_number: str = "Me") -> list[dict[str, str]]:
    with sqlite3.connect(db_location) as conn:
        cursor = conn.cursor()

        query = f"""\
            SELECT message.text, message.attributedBody, handle.id
            FROM message
            LEFT JOIN handle ON message.handle_id = handle.ROWID
            WHERE message.cache_roomnames == ?
        """

        results = cursor.execute(query, (chat_id,)).fetchall()
        messages: list[dict[str, str]] = []

        for result in results:
            text, attributed_body, handle_id = result

            if handle_id is None:
                phone_number = self_number
            else:
                phone_number = handle_id

            if text is not None:
                body = text
            elif attributed_body is None:
                continue
            else:
                attributed_body = attributed_body.decode("utf-8", errors="replace")

                if "NSNumber" in str(attributed_body):
                    attributed_body = str(attributed_body).split("NSNumber")[0]
                    if "NSString" in attributed_body:
                        attributed_body = str(attributed_body).split("NSString")[1]
                        if "NSDictionary" in attributed_body:
                            attributed_body = str(attributed_body).split("NSDictionary")[0]
                            attributed_body = attributed_body[6:-12]
                            body = attributed_body

            messages.append({"body": body, "phone_number": phone_number})  # type: ignore

        return messages


def get_chat_mapping(db_location: str, chat_name: str) -> str:
    with sqlite3.connect(db_location) as conn:
        cursor = conn.cursor()
        result: tuple[str] = cursor.execute("SELECT room_name FROM chat where display_name == ?", (chat_name,)).fetchone()

    return result[0]
