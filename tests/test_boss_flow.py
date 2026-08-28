import json

from hardcore.bosses import read_defeated_bosses
from hardcore.service import (
    format_boss_announcement,
    record_boss_defeat,
)
from hardcore.state import HardcoreState, load_state, save_state


def test_boss_flow_detects_records_and_persists(tmp_path):
    stats_directory = tmp_path / "world" / "stats"
    stats_directory.mkdir(parents=True)

    player_stats = {
        "stats": {
            "minecraft:killed": {
                "minecraft:ender_dragon": 1,
            }
        }
    }

    stats_file = stats_directory / "player.json"
    stats_file.write_text(
        json.dumps(player_stats),
        encoding="utf-8",
    )

    state = HardcoreState(
        run_number=6,
        status="RUNNING",
    )

    detected_bosses = read_defeated_bosses(stats_directory)

    assert detected_bosses == {"ender_dragon"}

    recorded = record_boss_defeat(
        state=state,
        boss_name="ender_dragon",
    )

    assert recorded is True

    state_path = tmp_path / "data" / "hardcore_state.json"
    save_state(state_path, state)

    restored_state = load_state(state_path)

    assert restored_state.bosses["ender_dragon"] is True
    assert record_boss_defeat(
        state=restored_state,
        boss_name="ender_dragon",
    ) is False

    announcement = format_boss_announcement(
        state=restored_state,
        boss_name="ender_dragon",
    )

    assert announcement == "Ender Dragon slain (1/4)"