from hardcore.monitor import ParsedDeath
from hardcore.service import format_death_announcement



def test_format_death_announcement():
    death = ParsedDeath(
        player="TestPlayer",
        cause="creeper",
        message="TestPlayer was blown up by Creeper",
    )

    result = format_death_announcement(run_number=6, death=death)

    expected = (
        "💀 Run 6 has ended!\n"
        "TestPlayer was blown up by Creeper."
    )

    assert result == expected