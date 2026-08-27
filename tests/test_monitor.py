from hardcore.monitor import read_new_log_lines
from hardcore.monitor import (
    ParsedDeath,
    parse_deaths_from_lines,
    read_new_log_lines,
)




def test_read_new_log_lines_only_returns_appended_content(tmp_path):
    log_path = tmp_path / "latest.log"
    log_path.write_text("old line\n", encoding="utf-8")

    old_lines, position = read_new_log_lines(log_path, 0)

    assert old_lines == ["old line\n"]

    with log_path.open("a", encoding="utf-8") as file:
        file.write("new line\n")

    new_lines, new_position = read_new_log_lines(log_path, position)

    assert new_lines == ["new line\n"]
    assert new_position > position

def test_read_new_log_lines_handles_missing_file(tmp_path):
    missing_path = tmp_path / "missing.log"
    
    lines, position = read_new_log_lines(missing_path, 0)

    assert lines == []
    assert position == 0
    assert not missing_path.exists()


def test_read_new_log_lines_handles_truncated_file(tmp_path):
    log_path = tmp_path / "latest.log"
    log_path.write_text(
        "this is a much longer old log line\n",
        encoding="utf-8",
    )

    old_lines, position = read_new_log_lines(log_path, 0)

    log_path.write_text("new line\n", encoding="utf-8")

    new_lines, new_position = read_new_log_lines(log_path, position)

    assert old_lines == ["this is a much longer old log line\n"]
    assert new_lines == ["new line\n"]
    assert new_position < position

def test_parse_deaths_from_lines_only_returns_deaths():
    lines = [
        "[21:30:00] [Server thread/INFO]: TestPlayer joined the game\n",
        "[21:31:00] [Server thread/INFO]: TestPlayer was blown up by Creeper\n",
        "[21:32:00] [Server thread/INFO]: TestPlayer left the game\n",
    ]

    deaths = parse_deaths_from_lines(lines)

    expected = [
        ParsedDeath(
            player="TestPlayer",
            cause="creeper",
            message="TestPlayer was blown up by Creeper",
        )
    ]

    assert deaths == expected