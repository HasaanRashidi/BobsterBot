from hardcore.monitor import ParsedDeath
from hardcore.state import DeathRecord, HardcoreState, default_boss_progress
from collections import Counter




def format_death_announcement(
        run_number: int,
        death: ParsedDeath,
) -> str:
    return (
        f"💀 Run {run_number} has ended!\n"
        f"{death.message}."
    )

def format_death_totals(state: HardcoreState) -> str:
    if not state.deaths:
        return "No Hardcore deaths have been recorded."

    death_totals = Counter(
        death.player for death in state.deaths
    )

    sorted_totals = sorted(
        death_totals.items(),
        key=lambda item: (-item[1], item[0].casefold()),
    )

    lines = ["Hardcore death totals:"]

    for player, total in sorted_totals:
        lines.append(f"{player}: {total}")

    return "\n".join(lines)

def format_death_log(
    state: HardcoreState,
    limit: int = 5,
) -> str:
    if not state.deaths:
        return "No Hardcore deaths have been recorded."

    safe_limit = max(1, limit)
    recent_deaths = state.deaths[-safe_limit:][::-1]

    lines = ["Recent Hardcore deaths:"]

    for death in recent_deaths:
        message = death.message.rstrip(".")
        lines.append(f"Run {death.run_number}: {message}.")

    return "\n".join(lines)

def format_player_death_stats(
    state: HardcoreState,
    player_name: str,
) -> str:
    cleaned_name = player_name.strip()

    matching_deaths = [
        death
        for death in state.deaths
        if death.player.casefold() == cleaned_name.casefold()
    ]

    if not matching_deaths:
        return f"No Hardcore deaths found for {cleaned_name}."

    display_name = matching_deaths[0].player

    cause_totals = Counter(
        death.cause for death in matching_deaths
    )

    sorted_causes = sorted(
        cause_totals.items(),
        key=lambda item: (-item[1], item[0].casefold()),
    )

    lines = [
        f"Hardcore stats for {display_name}:",
        f"Total deaths: {len(matching_deaths)}",
        "Causes:",
    ]

    for cause, total in sorted_causes:
        display_cause = cause.replace("_", " ").title()
        lines.append(f"{display_cause}: {total}")

    return "\n".join(lines)

def record_death(
        state: HardcoreState,
        death: ParsedDeath,
        timestamp: str
) -> DeathRecord | None:
    if state.status != "RUNNING":
        return None
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


def normalize_boss_name(boss_name: str) -> str:
    cleaned_name = boss_name.strip().lower().replace("-", " ")

    return "_".join(cleaned_name.split())


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


def format_boss_progress(state: HardcoreState) -> str:
    defeated_count = sum(state.bosses.values())
    total_bosses = len(state.bosses)

    lines = [
        f"Boss progress: {defeated_count}/{total_bosses}"
    ]

    for boss_name, defeated in state.bosses.items():
        marker = "✅" if defeated else "⬜"
        display_name = boss_name.replace("_", " ").title()
        lines.append(f"{marker} {display_name}")

    return "\n".join(lines)


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