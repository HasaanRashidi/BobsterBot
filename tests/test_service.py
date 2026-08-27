from hardcore.monitor import ParsedDeath
from hardcore.service import record_death
from hardcore.state import HardcoreState




def test_record_death_only_one_per_run():
    state = HardcoreState(
        run_number=6,
        status="RUNNING",
    )

    death = ParsedDeath(
        player="TestPlayer",
        cause="creeper",
        message="TestPlayer was blown up by creeper"
    )

    first_result = record_death(
        state=state,
        death=death,
        timestamp="2026-08-26T22:30:00Z",
    )

    second_result = record_death(
        state=state,
        death=death,
        timestamp="2026-08-26T22:30:01Z"
    )

    assert first_result is not None
    assert second_result is None
    assert state.status == "DEAD"
    assert len(state.deaths) == 1
    assert state.deaths[0].run_number == 6