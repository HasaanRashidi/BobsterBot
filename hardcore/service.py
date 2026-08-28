from hardcore.monitor import ParsedDeath
from hardcore.state import DeathRecord, HardcoreState, default_boss_progress




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


def format_boss_announcement(
        state: HardcoreState,
        boss_name: str,
) -> str:
    display_name = boss_name.replace("_", " ").title()
    defeated_count = sum(state.bosses.values())
    total_bosses = len(state.bosses)

    return (
        f"{display_name} slain "
        f"({defeated_count}/{total_bosses})"
    )


def record_boss_defeat(
        state: HardcoreState,
        boss_name: str,
) -> bool:
    if state.status != "RUNNING":
        return False

    if boss_name not in state.bosses:
        return False
    
    if state.bosses[boss_name]:
        return False
    
    state.bosses[boss_name] = True
    return True


def prepare_next_run(state: HardcoreState) -> bool:
    if state.status != "DEAD":
        return False

    state.run_number += 1
    state.status = "STOPPED"
    state.world_folder = "world"
    state.bosses = default_boss_progress()

    return True