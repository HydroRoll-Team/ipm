from pathlib import Path
import tarfile
import shutil
import os.path as path

from ipm.models.ipk import InfiniProject


def create_tar_gz(source_folder: str, output_filepath: str) -> None:
    shutil.move(
        shutil.make_archive(output_filepath + ".build", "gztar", source_folder),
        output_filepath,
        shutil.copy2,
    )


def extract_tar_gz(input_filename: str, output_folder: str) -> None:
    with tarfile.open(input_filename, "r:gz") as tar:
        tar.extractall(output_folder, filter=tarfile.fully_trusted_filter)


def create_xml_file(meta_data: InfiniProject, output_folder: str | Path) -> None:
    from collections import defaultdict

    meta_data_dict = defaultdict(
        lambda: "", meta_data._data.get("project")  # type: ignore
    )

    with open(
        path.join(output_folder, f"{meta_data.name}.xml"), mode="w", encoding="utf8"
    ) as xml_file:
        xml_file.write(
            """<package id="{name}"
        name="{name}: {description}"
        webpage="{webpage}"
        author="{authors[0][name]}"
        license="{license}"
        unzip="{unzip}"/>""".format(
                **meta_data_dict
            )
        )
