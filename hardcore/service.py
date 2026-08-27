from hardcore.monitor import ParsedDeath
from hardcore.state import DeathRecord, HardcoreState




def format_death_announcement(
        run_number: int,
        death: ParsedDeath,
) -> str:
    return (
        f"💀 Run {run_number} has ended!\n"
        f"{death.message}."
    )

def record_death(
        state: HardcoreState,
        death: ParsedDeath,
        timestamp: str
) -> DeathRecord | None:
    already_recorded = any(
        existing_death.run_number == state.run_number
        for existing_death in state.deaths
    )

    if already_recorded:
        return None

    record = DeathRecord(
        run_number=state.run_number,
        player=death.player,
        cause=death.cause,
        message=death.message,
        timestamp=timestamp,
    )

    state.deaths.append(record)
    state.status = "DEAD"

    return record