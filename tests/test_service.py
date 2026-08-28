from hardcore.monitor import ParsedDeath
from hardcore.service import (
    record_death,
    prepare_next_run,
    record_boss_defeat,
    format_boss_announcement,
    format_boss_progress,
    normalize_boss_name,
    format_death_totals,
    format_death_log,
    format_player_death_stats,
)
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


def test_record_boss_defeat_marks_boss_complete():
    state = HardcoreState(run_number=6, status="RUNNING")

    result = record_boss_defeat(
        state=state,
        boss_name="ender_dragon",
    )

    assert result is True
    assert state.bosses["ender_dragon"] is True


def test_record_boss_defeat_only_records_once():
    state = HardcoreState(run_number=6, status="RUNNING")

    first_result = record_boss_defeat(
        state=state,
        boss_name="ender_dragon",
    )

    second_result = record_boss_defeat(
        state=state,
        boss_name="ender_dragon",
    )

    assert first_result is True
    assert second_result is False
    assert state.bosses["ender_dragon"] is True


def test_record_boss_defeat_refuses_inactive_run():
    state = HardcoreState(run_number=6, status="STOPPED")

    result = record_boss_defeat(
        state=state,
        boss_name="ender_dragon",
    )

    assert result is False
    assert state.bosses["ender_dragon"] is False


def test_record_boss_defeat_rejects_unknown_boss():
    state = HardcoreState(run_number=6, status="RUNNING")

    result = record_boss_defeat(
        state=state,
        boss_name="herobrine"
    )

    assert result is False
    assert "herobrine" not in state.bosses


def test_format_boss_announcement_includes_progress():
    state = HardcoreState(run_number=6, status="RUNNING")
    state.bosses["ender_dragon"] = True

    result = format_boss_announcement(
        state=state,
        boss_name="ender_dragon",
    )

    assert result == "Ender Dragon slain (1/4)"


def test_format_boss_progress_lists_all_bosses():
    state = HardcoreState(run_number=6, status="RUNNING")
    state.bosses["ender_dragon"] = True

    result = format_boss_progress(state)

    assert result == (
        "Boss progress: 1/4\n"
        "✅ Ender Dragon\n"
        "⬜ Wither\n"
        "⬜ Warden\n"
        "⬜ Elder Guardian"
    )


def test_normalize_boss_name_accepts_display_name():
    result = normalize_boss_name("  Ender Dragon  ")

    assert result == "ender_dragon"


def test_format_death_totals_counts_each_player():
    state = HardcoreState(
        deaths=[
            DeathRecord(
                run_number=1,
                player="Alex",
                cause="creeper",
                message="Alex was blown up by Creeper",
                timestamp="2026-01-01T12:00:00Z",
            ),
            DeathRecord(
                run_number=2,
                player="Steve",
                cause="skeleton",
                message="Steve was shot by Skeleton",
                timestamp="2026-01-02T12:00:00Z",
            ),
            DeathRecord(
                run_number=3,
                player="Alex",
                cause="fall",
                message="Alex fell from a high place",
                timestamp="2026-01-03T12:00:00Z",
            ),
        ]
    )

    result = format_death_totals(state)

    assert result == (
        "Hardcore death totals:\n"
        "Alex: 2\n"
        "Steve: 1"
    )


def test_format_death_totals_handles_empty_history():
    state = HardcoreState()

    result = format_death_totals(state)

    assert result == "No Hardcore deaths have been recorded."


def test_format_death_log_shows_newest_deaths_first():
    state = HardcoreState(
        deaths=[
            DeathRecord(
                run_number=1,
                player="Alex",
                cause="creeper",
                message="Alex was blown up by Creeper",
                timestamp="2026-01-01T12:00:00Z",
            ),
            DeathRecord(
                run_number=2,
                player="Steve",
                cause="skeleton",
                message="Steve was shot by Skeleton",
                timestamp="2026-01-02T12:00:00Z",
            ),
            DeathRecord(
                run_number=3,
                player="Alex",
                cause="fall",
                message="Alex fell from a high place",
                timestamp="2026-01-03T12:00:00Z",
            ),
        ]
    )

    result = format_death_log(state, limit=2)

    assert result == (
        "Recent Hardcore deaths:\n"
        "Run 3: Alex fell from a high place.\n"
        "Run 2: Steve was shot by Skeleton."
    )


def test_format_death_log_handles_empty_history():
    state = HardcoreState()

    result = format_death_log(state)

    assert result == "No Hardcore deaths have been recorded."


def test_format_player_death_stats_counts_causes():
    state = HardcoreState(
        deaths=[
            DeathRecord(
                run_number=1,
                player="Alex",
                cause="creeper",
                message="Alex was blown up by Creeper",
                timestamp="2026-01-01T12:00:00Z",
            ),
            DeathRecord(
                run_number=2,
                player="Steve",
                cause="skeleton",
                message="Steve was shot by Skeleton",
                timestamp="2026-01-02T12:00:00Z",
            ),
            DeathRecord(
                run_number=3,
                player="Alex",
                cause="fall",
                message="Alex fell from a high place",
                timestamp="2026-01-03T12:00:00Z",
            ),
        ]
    )

    result = format_player_death_stats(state, "  aLeX  ")

    assert result == (
        "Hardcore stats for Alex:\n"
        "Total deaths: 2\n"
        "Causes:\n"
        "Creeper: 1\n"
        "Fall: 1"
    )


def test_format_player_death_stats_handles_unknown_player():
    state = HardcoreState()

    result = format_player_death_stats(state, "Herobrine")

    assert result == "No Hardcore deaths found for Herobrine."