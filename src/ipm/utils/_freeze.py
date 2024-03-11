from curses import meta
from importlib import metadata
from pathlib import Path
from struct import pack
import tarfile
import shutil
import os.path as path

from ipm.models.ipk import InfiniProject


def create_tar_gz(source_folder: str, output_filepath: str) -> None:
    shutil.move(
        shutil.make_archive(output_filepath + ".build",
                            "gztar", source_folder),
        output_filepath,
        shutil.copy2,
    )


def extract_tar_gz(input_filename: str, output_folder: str) -> None:
    with tarfile.open(input_filename, "r:gz") as tar:
        tar.extractall(output_folder, filter=tarfile.fully_trusted_filter)


def create_xml_file(meta_data: InfiniProject, output_folder: str | Path) -> None:
    package = {}
    package['_id'] = meta_data.name
    package['version'] = meta_data.version
    package['description'] = meta_data.description
    authors = meta_data.authors
    if authors is not None:
        package['author'] = authors.first
    package['_license'] = meta_data.license
    package['webpage'] = meta_data.webpage
    package['unzip'] = meta_data.unzip

    with open(path.join(output_folder, package["_id"], ".xml"), mode='w', encoding='utf8') as xml_file:
        xml_file.write(f"""<package id="{_id}"
        name="{_id}: {description}"
        webpage="{webpage}"
        author="{author}"
        license="{_license}"
        unzip="{unzip}"/>""".format(**package))
