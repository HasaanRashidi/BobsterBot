import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ParsedDeath:
    player: str
    cause: str
    message: str

KILLER_DEATH_PHRASES = (
    " was blown up by ",
    " was shot by ",
    " was slain by ",
)

PLAYER_NAME_PATTERN = re.compile(r"[A-Za-z0-9_]{1,16}")


def is_valid_player_name(player_name: str) -> bool:
    return PLAYER_NAME_PATTERN.fullmatch(player_name) is not None


def parse_death_message(log_line: str) -> ParsedDeath | None:

    prefix, separator, message = log_line.partition("]: ")

    if not separator:
        return None

    message = message.strip()

    for death_phrase in KILLER_DEATH_PHRASES:
        player, death_separator, killer = message.partition(death_phrase)

        if death_separator and is_valid_player_name(player):
            return ParsedDeath(
                player=player,
                cause=killer.lower(),
                message=message,
            )

    for death_suffix, cause in FIXED_CAUSE_DEATH_SUFFIXES:
        if message.endswith(death_suffix):
            player = message.removesuffix(death_suffix)

            if not is_valid_player_name(player):
                continue

            return ParsedDeath(
                player=player,
                cause=cause,
                message=message,
            )

    return None

FIXED_CAUSE_DEATH_SUFFIXES = (
    (" fell from a high place", "fall"),
    (" drowned", "drowning"),
    (" burned to death", "fire"),
    (" tried to swim in lava", "lava"),
    (" hit the ground too hard", "fall"),
    (" suffocated in a wall", "suffocation"),
)

def parse_deaths_from_lines(lines: list[str]) -> list[ParsedDeath]:
    deaths = []

    for line in lines:
        death = parse_death_message(line)

        if death is not None:
            deaths.append(death)

    return deaths


def read_new_log_lines(
    log_path: Path,
    position: int,
) -> tuple[list[str], int]:
    original_position = position

    try:
        if not log_path.exists():
            return [], position

        with log_path.open("r", encoding="utf-8") as file:
            file.seek(0, 2)
            end_position = file.tell()

            if position > end_position:
                position = 0

            file.seek(position)
            lines = file.readlines()
            new_position = file.tell()

    except OSError:
        return [], original_position

    return lines, new_position
