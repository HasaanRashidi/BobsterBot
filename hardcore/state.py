import json
from pathlib import Path
from dataclasses import dataclass, field, asdict

# frozen means its immutable after creation (cant be changed)
@dataclass(frozen=True)
class DeathRecord:
    """Record information about a players death."""
    run_number: int
    player: str
    cause: str
    message: str
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict) -> "DeathRecord":
        """Create a death record from dictionary data."""
        return cls(**data)

BOSS_NAMES = ("ender_dragon", "wither", "warden", "elder_guardian")

def default_boss_progress() -> dict[str, bool]:
    """Return a fresh completion map for all tracked bosses."""
    return {boss: False for boss in BOSS_NAMES}

@dataclass
class HardcoreState:
    """Store persistent information about the current Hardcore run."""
    schema_version: int = 1
    run_number: int = 1
    status: str = "STOPPED"
    world_folder: str = "world"
    deaths: list[DeathRecord] = field(default_factory=list)
    bosses: dict[str, bool] = field(default_factory=default_boss_progress)

    def to_dict(self) -> dict:
        """Convert the state into a JSON-compatible dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "HardcoreState":
        """Create Hardcore state from dictionary data loaded from JSON."""
        deaths = [
            DeathRecord.from_dict(death_data) for death_data in data.get("deaths", [])
        ]

        return cls(
            schema_version=data.get("schema_version", 1),
            run_number=data.get("run_number", 1),
            status=data.get("status", "STOPPED"),
            world_folder=data.get("world_folder", "world"),
            deaths=deaths,
            bosses=data.get("bosses", default_boss_progress()),
        )

def save_state(path: Path, state: HardcoreState) -> None:
    """Save Hardcore state to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(state.to_dict(), file, indent=2)

def load_state(path: Path) -> HardcoreState:
    """Load Hardcore state from JSON, or return a default state if missing."""
    if not path.exists():
        return HardcoreState()

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return HardcoreState.from_dict(data)