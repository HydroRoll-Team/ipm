import tarfile
import shutil


def create_tar_gz(source_folder: str, output_filepath: str) -> None:
    shutil.move(
        shutil.make_archive(output_filepath + ".build", "gztar", source_folder),
        output_filepath,
        shutil.copy2,
    )


def extract_tar_gz(input_filename: str, output_folder: str) -> None:
    with tarfile.open(input_filename, "r:gz") as tar:
        tar.extractall(output_folder, filter=tarfile.fully_trusted_filter)
