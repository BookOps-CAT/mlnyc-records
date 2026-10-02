import datetime
import json
import logging
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from mlnyc_records.build import TeacherSetBuilder

logger = logging.getLogger(__name__)


def create_file_list(path: str | None = "data/json") -> list[Path]:
    dir_path = Path(path)
    return [i for i in dir_path.iterdir() if i.is_file()]


def read_json_files(file_list: list[Path]) -> list[dict[str, Any]]:
    files = []
    for file_path in file_list:
        with open(file_path, "rb") as fh:
            json_data = json.load(fh)
            taxonomies = defaultdict(list)
            for taxonomy in json_data["taxonomies"]:
                values = taxonomy["values"]
                if isinstance(values, list):
                    taxonomies[taxonomy["name"]].extend(values)
                else:
                    taxonomies[taxonomy["name"]].append(values)
            items = []
            special_formats = []
            for item in json_data["items"]:
                item_data = {
                    "copies": item["copies"],
                    "isbn": item["isbn"],
                    "format": item["format"],
                    "title": item["title"],
                }
                if item["format"] in ["puppets", "textile"]:
                    special_formats.append(item_data)
                else:
                    items.append(item_data)
            files.append(
                {
                    "set_title": json_data["curation_list_name"],
                    "copies_of_set": json_data["copies_to_procure"],
                    "items": items,
                    "local_genre_term": taxonomies.get("genre", []),
                    "local_topic_term": taxonomies.get("topic", []),
                    "grade_level": taxonomies["grade"][0],
                    "subject": taxonomies["subject"][0],
                    "set_type": taxonomies["set_type"][0],
                    "language": taxonomies["language"][0],
                }
            )
    return files


def build_records(outfile: str | None = None):
    builder = TeacherSetBuilder()
    today_str = datetime.datetime.strftime(datetime.date.today(), "%y%m%d")
    outfile = f"data/marc/{today_str}_PROCESSED.mrc"
    file_list = create_file_list()
    set_data = read_json_files(file_list=file_list)
    for set_json in set_data:
        control_number = builder.ctrl_number_gen.next_control_number()
        try:
            teacher_set = builder.build_teacher_set(**set_json)
        except ValidationError as e:
            logger.error(f"Validation errors for set: {e.json()}.")
        else:
            valid_set_copies = builder.build_set_copies(
                teacher_set, control_number=control_number
            )
            builder.write_marc_to_file(set_bibs=valid_set_copies, out_file=outfile)
            builder.ctrl_number_gen.save_state()
    for file in file_list:
        destination_dir = Path("data/processed")
        shutil.move(file, destination_dir / file.name)
