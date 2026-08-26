from hardcore.monitor import ParsedDeath, parse_death_message


def test_parse_creeper_death():
    log_line = (
        "[21:30:00] [Server thread/INFO]: "
        "TestPlayer was blown up by Creeper"
    )

    result = parse_death_message(log_line)

    expected = ParsedDeath(
        player="TestPlayer",
        cause="creeper",
        message="TestPlayer was blown up by Creeper",
    )

    assert result == expected




def test_ignore_non_death_message():
    log_line = (
        "[21:30:00] [Server thread/INFO]: "
        "TestPlayer joined the game"
    )

    result = parse_death_message(log_line)

    assert result is None

def test_parse_skeleton_death():
    log_line = (
        "[21:30:00] [Server thread/INFO]: "
        "TestPlayer was shot by Skeleton"
    )

    result = parse_death_message(log_line)

    expected = ParsedDeath(
        player="TestPlayer",
        cause="skeleton",
        message="TestPlayer was shot by Skeleton",
    )

    assert result == expected

def test_parse_fall_death():
    log_line = (
        "[21:30:00] [Server thread/INFO]: "
        "TestPlayer fell from a high place"
    )

    result = parse_death_message(log_line)

    expected = ParsedDeath(
        player="TestPlayer",
        cause="fall",
        message="TestPlayer fell from a high place",
    )

    assert result == expected

def test_parse_zombie_death():
    log_line = (
        "[21:30:00] [Server thread/INFO]: "
        "TestPlayer was slain by Zombie"
    )

    result = parse_death_message(log_line)

    expected = ParsedDeath(
        player="TestPlayer",
        cause="zombie",
        message="TestPlayer was slain by Zombie"
    )

    assert result == expected