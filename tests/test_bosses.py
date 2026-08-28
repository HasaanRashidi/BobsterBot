import json

from hardcore.bosses import read_defeated_bosses





def test_read_defeated_bosses_from_player_stats(tmp_path):
    stats_directory = tmp_path / "stats"
    stats_directory.mkdir()

    player_stats = {
        "stats": {
            "minecraft:killed": {
                "minecraft:ender_dragon": 1,
                "minecraft:zombie": 12,
            }
        }
    }

    stats_file = stats_directory / "player.json"
    stats_file.write_text(
        json.dumps(player_stats),
        encoding="utf-8",
    )

    result = read_defeated_bosses(stats_directory)

    assert result == {"ender_dragon"}


def test_read_defeated_bosses_ignored_malformed_file(tmp_path):
    stats_directory = tmp_path / "stats"
    stats_directory.mkdir()

    broken_file = stats_directory / "broken.json"
    broken_file.write_text(
        "{not valid json}",
        encoding="utf-8",
    )

    result = read_defeated_bosses(stats_directory)

    assert result == set()
    