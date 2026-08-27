from hardcore.monitor import ParsedDeath
from hardcore.service import record_death, prepare_next_run
from hardcore.state import HardcoreState, DeathRecord




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

def test_prepare_next_run_preserves_history_and_resets_progress():
    state = HardcoreState(run_number=6, status="DEAD")

    old_death = DeathRecord(
        run_number=5,
        player="FrankoDravis",
        cause="creeper",
        message="Frankodravis was blown up by Creeper",
        timestamp="2026-08-24",
        )

    state.deaths.append(old_death)
    state.bosses["warden"] = True
    result = prepare_next_run(state)

    assert result is True
    assert state.run_number == 7
    assert state.status == "STOPPED"
    assert state.deaths == [old_death]
    assert all(defeated is False for defeated in state.bosses.values())


def test_prepare_next_run_refuses_active_run():
    state=HardcoreState(run_number=6, status="RUNNING")

    result = prepare_next_run(state)

    assert result is False
    assert state.run_number == 6
    assert state.status == "RUNNING"