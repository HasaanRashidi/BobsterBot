from io import StringIO
from unittest.mock import Mock


from hardcore.config import HardcoreConfig
from hardcore.server import HardcoreServerManager




def test_send_command_writes_to_minecraft_console(tmp_path):
    config = HardcoreConfig(
        server_directory=tmp_path,
        java_executable=tmp_path / "java.exe",
    )
    manager = HardcoreServerManager(config)

    fake_process = Mock()
    fake_process.poll.return_value = None
    fake_process.stdin = StringIO()
    manager._process = fake_process

    manager.send_command("say Ender Dragon slain (1/4)")

    assert (
        fake_process.stdin.getvalue()
        == "say Ender Dragon slain (1/4)\n"
    )