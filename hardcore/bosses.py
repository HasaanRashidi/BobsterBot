import json
from pathlib import Path

from hardcore.state import BOSS_NAMES






def read_defeated_bosses(stats_directory: Path) -> set[str]:
    defeated_bosses: set[str] = set()

    if not stats_directory.is_dir():
        return defeated_bosses

    for stats_file in stats_directory.glob("*.json"):
        try:
            data = json.loads(
                stats_file.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            continue

        killed_entities = (
            data.get("stats", {})
            .get("minecraft:killed", {})
        )

        for boss_name in BOSS_NAMES:
            entity_name = f"minecraft:{boss_name}"

            if killed_entities.get(entity_name, 0) > 0:
                defeated_bosses.add(boss_name)

    return defeated_bosses