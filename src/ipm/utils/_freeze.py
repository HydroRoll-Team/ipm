from pathlib import Path
from ipm.models.ipk import InfiniProject
from ipm.typing import StrPath

import sys
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
        if sys.version_info >= (3, 12):
            tar.extractall(output_folder, filter=tarfile.fully_trusted_filter)
        else:
            tar.extractall(output_folder)


def create_xml_file(meta_data: InfiniProject, output_folder: StrPath) -> None:
    from collections import defaultdict

    meta_data_dict = defaultdict(
        lambda: "", meta_data._data.get("project")  # type: ignore
    )

    Path(output_folder).joinpath(f"{meta_data.name}.xml").write_text(
        """<package id="{name}"
        name="{name}: {description}"
        webpage="{webpage}"
        author="{authors[0][name]}"
        license="{license}"
        unzip="{unzip}"/>""".format(
            **meta_data_dict
        ),
        encoding="utf-8",
    )
