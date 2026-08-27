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

def parse_death_message(log_line: str) -> ParsedDeath | None:

    prefix, separator, message = log_line.partition("]: ")

    if not separator:
        return None

    message = message.strip()

    for death_phrase in KILLER_DEATH_PHRASES:
        player, death_separator, killer = message.partition(death_phrase)

        if death_separator:
            return ParsedDeath(
                player=player,
                cause=killer.lower(),
                message=message,
            )

    for death_suffix, cause in FIXED_CAUSE_DEATH_SUFFIXES:
        if message.endswith(death_suffix):
            player = message.removesuffix(death_suffix)

            return ParsedDeath(
                player=player,
                cause=cause,
                message=message,
            )

    return None

FIXED_CAUSE_DEATH_SUFFIXES = (
    (" fell from a high place", "fall"),
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

    return lines, new_position