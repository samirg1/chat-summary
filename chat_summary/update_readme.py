from chat_summary.get_available_games import get_available_chat_games


def update_readme() -> None:
    new_contents: list[str] = []
    with open("README.md") as f:
        contents = f.readlines()
        options_start = next(i for i, line in enumerate(contents) if line == "#### Options\n")
        new_contents.extend(contents[: options_start + 4])

        for name, _ in get_available_chat_games():
            new_contents.append(f"- '-{name[0]}', '--{name}': Include the '{name}' game in the results\n")
        new_contents.append("\n")

        output_start = next(i for i, line in enumerate(contents) if line == "### Output\n")
        new_contents.extend(contents[output_start:])

    with open("README.md", "w") as f:
        f.writelines(new_contents)
