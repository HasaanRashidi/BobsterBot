from hardcore.monitor import ParsedDeath, parse_death_message
import pytest


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


def test_ignore_villager_entity_death():
    log_line = (
        "[21:30:00] [Server thread/INFO]: "
        "Villager Villager['Villager'/154, l='ServerLevel[world]', "
        "x=47.25, y=48.00, z=-152.01] died, message: "
        "'Villager was slain by Zombie'"
    )

    result = parse_death_message(log_line)

    assert result is None


def test_parse_drowning_death():
    line = (
        "[12:00:00] [Server thread/INFO]: "
        "TestPlayer drowned"
    )

    death = parse_death_message(line)

    expected = ParsedDeath(
        player="TestPlayer",
        cause="drowning",
        message="TestPlayer drowned",
    )

    assert death == expected


@pytest.mark.parametrize(
    ("message", "cause"),
    [
        ("TestPlayer burned to death", "fire"),
        ("TestPlayer tried to swim in lava", "lava"),
        ("TestPlayer hit the ground too hard", "fall"),
        ("TestPlayer suffocated in a wall", "suffocation"),
    ],
)
def test_parse_environmental_deaths(message, cause):
    line = f"[12:00:00] [Server thread/INFO]: {message}"

    death = parse_death_message(line)

    expected = ParsedDeath(
        player="TestPlayer",
        cause=cause,
        message=message,
    )

    assert death == expected
