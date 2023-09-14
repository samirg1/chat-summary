import pytest

from chat_summary.chat_summary import main


@pytest.fixture
def wordle(capsys: pytest.CaptureFixture[str]) -> str:
    main(["samir", "Wordle Crew", "-W"])
    return capsys.readouterr().out


@pytest.mark.parametrize("text", ("WORDLE", "COMPLETIONS", "AVERAGE GUESSES"))
def test_summary_wordle(text: str, wordle: str):
    assert text in wordle
