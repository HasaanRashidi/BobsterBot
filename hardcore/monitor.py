from dataclasses import dataclass

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