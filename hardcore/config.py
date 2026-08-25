"""Configuration for the temporary, playable Hardcore server."""

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class HardcoreConfig:
    """Paths and network settings that are separate from the old server."""

    server_directory: Path
    java_executable: Path
    port: int = 25565
    minimum_memory: str = "2G"
    maximum_memory: str = "4G"

    @property
    def server_jar(self) -> Path:
        return self.server_directory / "server.jar"

    @classmethod
    def from_environment(cls) -> "HardcoreConfig":
        project_root = Path(__file__).resolve().parent.parent
        default_server_directory = project_root / "hardcore_server"
        return cls(
            server_directory=Path(
                os.getenv("HC_SERVER_DIRECTORY", default_server_directory)
            ),
            java_executable=Path(
                os.getenv(
                    "HC_JAVA_EXECUTABLE",
                    default_server_directory
                    / "runtime"
                    / "jdk-25.0.4.1+1-jre"
                    / "bin"
                    / "java.exe",
                )
            ),
            port=int(os.getenv("HC_SERVER_PORT", "25565")),
            minimum_memory=os.getenv("HC_MIN_MEMORY", "2G"),
            maximum_memory=os.getenv("HC_MAX_MEMORY", "4G"),
        )
