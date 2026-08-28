from pathlib import Path
import shutil




PRIMARY_WORLD_FOLDER = "world"
SPLIT_DIMENSION_FOLDERS = ("world_nether", "world_the_end")


def archive_worlds(
        server_directory: Path,
        archive_directory: Path,
        run_number: int,
) -> Path:
    archive_path = archive_directory / f"run-{run_number:03d}"

    if archive_path.exists():
        raise FileExistsError(f"Archive already exists: {archive_path}")

    primary_world_path = server_directory / PRIMARY_WORLD_FOLDER

    if not primary_world_path.is_dir():
        raise FileNotFoundError(
            f"Missing world folder: {primary_world_path}"
        )

    split_dimension_paths = [
        server_directory / folder_name
        for folder_name in SPLIT_DIMENSION_FOLDERS
    ]
    split_dimensions_present = [
        path.is_dir()
        for path in split_dimension_paths
    ]

    if any(split_dimensions_present) and not all(split_dimensions_present):
        missing_path = next(
            path
            for path, is_present in zip(
                split_dimension_paths,
                split_dimensions_present,
            )
            if not is_present
        )
        raise FileNotFoundError(
            f"Missing world folder: {missing_path}"
        )

    source_paths = [primary_world_path]

    if all(split_dimensions_present):
        source_paths.extend(split_dimension_paths)

    archive_path.mkdir(parents=True)
    moved_paths = []

    try:
        for source_path in source_paths:
            destination_path = archive_path / source_path.name
            shutil.move(str(source_path), str(destination_path))
            moved_paths.append((source_path, destination_path))

    except Exception:
        for source_path, destination_path in reversed(moved_paths):
            if destination_path.exists() and not source_path.exists():
                shutil.move(
                    str(destination_path),
                    str(source_path),
                )

        if archive_path.exists():
            shutil.rmtree(archive_path)

        raise

    return archive_path