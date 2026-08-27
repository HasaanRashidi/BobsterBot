from hardcore.worlds import archive_worlds
import pytest




def test_archive_worlds_moves_all_dimensions(tmp_path):
    server_directory = tmp_path / "server"
    archive_directory = tmp_path/ "archives"
    server_directory.mkdir()

    world_names = ("world", "world_nether", "world_the_end")

    for world_name in world_names:
        world_path = server_directory / world_name
        world_path.mkdir()
        (world_path / "marker.txt").write_text(
            world_name,
            encoding="utf-8"
        )

    archive_path = archive_worlds(
        server_directory=server_directory,
        archive_directory=archive_directory,
        run_number=6,
    )

    assert archive_path == archive_directory / "run-006"

    for world_name in world_names:
        assert not (server_directory / world_name).exists()

        marker_path = archive_path / world_name / "marker.txt"
        assert marker_path.read_text(encoding="utf-8") == world_name


def test_archive_worlds_refuses_existing_archive(tmp_path):
    server_directory = tmp_path / "server"
    archive_directory = tmp_path / "archives"
    server_directory.mkdir()

    world_names = ("world", "world_nether", "world_the_end")

    for world_name in world_names:
        (server_directory / world_name).mkdir()

    existing_archive = archive_directory / "run-006"
    existing_archive.mkdir(parents=True)

    with pytest.raises(FileExistsError):
        archive_worlds(
            server_directory=server_directory,
            archive_directory=archive_directory,
            run_number=6,
        )

    for world_name in world_names:
        assert (server_directory / world_name).exists()


def test_archive_worlds_refuses_missing_dimension(tmp_path):
    server_directory = tmp_path / "server"
    archive_directory = tmp_path / "archives"
    server_directory.mkdir()

    (server_directory / "world").mkdir()
    (server_directory / "world_nether").mkdir()
    # Deliberately do not create world_the_end

    with pytest.raises(FileNotFoundError):
        archive_worlds(
            server_directory=server_directory,
            archive_directory=archive_directory,
            run_number=6,
        )

    assert (server_directory / "world").exists()
    assert (server_directory / "world_nether").exists()
    assert not (archive_directory / "run-006").exists()