from dataclasses import dataclass, field, asdict

# frozen means its immutable after creation (cant be changed)
@dataclass(frozen=True)
class DeathRecord:
    run_number: int
    player: str
    cause: str
    message: str
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict) -> "DeathRecord":
        return cls(**data)

BOSS_NAMES = ("ender_dragon", "wither", "warden", "elder_guardian")

def default_boss_progress() -> dict[str, bool]:
    return {boss: False for boss in BOSS_NAMES}

@dataclass
class HardcoreState:
    schema_version: int = 1
    run_number: int = 1
    status: str = "STOPPED"
    world_folder: str = "world"
    deaths: list[DeathRecord] = field(default_factory=list)
    bosses: dict[str, bool] = field(default_factory=default_boss_progress)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "HardcoreState":
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

