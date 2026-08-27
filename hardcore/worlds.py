from pathlib import Path
import shutil




WORLD_FOLDERS = ("world", "world_nether", "world_the_end")


def archive_worlds(
        server_directory: Path,
        archive_directory: Path,
        run_number: int,
) -> Path:
    archive_path = archive_directory / f"run-{run_number:03d}"

    if archive_path.exists():
        raise FileExistsError(f"Archive already exists: {archive_path}")

    source_paths = [
        server_directory / world_name
        for world_name in WORLD_FOLDERS
    ]

    for source_path in source_paths:
        if not source_path.is_dir():
            raise FileNotFoundError(
                f"Missing world folder: {source_path}"
            )

    archive_path.mkdir(parents=True)

    for source_path in source_paths:
        destination_path = archive_path / source_path.name
        shutil.move(str(source_path), str(destination_path))

    return archive_path