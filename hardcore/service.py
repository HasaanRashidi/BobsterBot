from hardcore.monitor import ParsedDeath




def format_death_announcement(
        run_number: int,
        death: ParsedDeath,
) -> str:
    return (
        f"💀 Run {run_number} has ended!\n"
        f"{death.message}."
    )