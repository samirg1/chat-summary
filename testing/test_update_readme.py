from chat_summary.update_readme import update_readme


def test_check_solaris_version():
    expected: list[str] = []
    with open("README.md") as new:
        expected.extend(new.readlines())
        
    with open("testing/test.md") as old:
        with open("README.md", "w") as new:
            new.writelines(old.readlines())
    update_readme()
    with open("README.md") as new:
        assert new.readlines() == expected
