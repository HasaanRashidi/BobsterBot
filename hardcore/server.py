"""Minimal process manager for the temporary vanilla Hardcore server."""

from __future__ import annotations

import socket
import subprocess
import threading
import time
from typing import TextIO

from .config import HardcoreConfig


class HardcoreServerManager:
    """Start and gracefully stop one Hardcore Minecraft process."""

    def __init__(self, config: HardcoreConfig):
        self.config = config
        self._process: subprocess.Popen[str] | None = None
        self._log_file: TextIO | None = None
        self._lock = threading.Lock()

    def is_online(self, timeout: float = 1.0) -> bool:
        try:
            with socket.create_connection(("127.0.0.1", self.config.port), timeout):
                return True
        except OSError:
            return False

    def is_process_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self) -> int:
        with self._lock:
            if self.is_process_running() or self.is_online():
                raise RuntimeError("The Hardcore server is already running.")

            if not self.config.java_executable.is_file():
                raise FileNotFoundError(
                    f"Java was not found at {self.config.java_executable}"
                )
            if not self.config.server_jar.is_file():
                raise FileNotFoundError(
                    f"Minecraft server.jar was not found at {self.config.server_jar}"
                )

            logs_directory = self.config.server_directory / "logs"
            logs_directory.mkdir(parents=True, exist_ok=True)
            self._log_file = (logs_directory / "bobster-console.log").open(
                "a", encoding="utf-8", buffering=1
            )

            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            self._process = subprocess.Popen(
                [
                    str(self.config.java_executable),
                    f"-Xms{self.config.minimum_memory}",
                    f"-Xmx{self.config.maximum_memory}",
                    "-jar",
                    str(self.config.server_jar),
                    "nogui",
                ],
                cwd=self.config.server_directory,
                stdin=subprocess.PIPE,
                stdout=self._log_file,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False,
                creationflags=creation_flags,
            )
            return self._process.pid

    def wait_until_online(self, timeout: float = 120.0) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.is_online():
                return True
            if self._process is not None and self._process.poll() is not None:
                return False
            time.sleep(1)
        return False

    def stop(self, timeout: float = 60.0) -> None:
        with self._lock:
            if not self.is_process_running():
                if self.is_online():
                    raise RuntimeError(
                        "Minecraft is online, but this Bobster session did not start it. "
                        "Stop it from its console for now."
                    )
                raise RuntimeError("The Hardcore server is not running.")

            assert self._process is not None
            assert self._process.stdin is not None
            self._process.stdin.write("save-all flush\n")
            self._process.stdin.flush()
            self._process.stdin.write("stop\n")
            self._process.stdin.flush()

        try:
            self._process.wait(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "Minecraft did not stop within the expected time; it was left running."
            ) from exc
        finally:
            if self._process.poll() is not None:
                self._process = None
                if self._log_file is not None:
                    self._log_file.close()
                    self._log_file = None
