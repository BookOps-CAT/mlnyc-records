import datetime
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from mlnyc_records.build import TeacherSetBuilder

logger = logging.getLogger(__name__)


def read_app_json(path: str | None = "data/new/json") -> list[dict[str, Any]]:
    dir_path = Path(path)
    files = []
    file_paths = [i for i in dir_path.iterdir() if i.is_file()]
    for file_path in file_paths:
        with open(file_path, "rb") as fh:
            json_data = json.load(fh)
            taxonomies = defaultdict(list)
            for taxonomy in json_data["taxonomies"]:
                values = taxonomy["values"]
                if isinstance(values, list):
                    taxonomies[taxonomy["name"]].extend(values)
                else:
                    taxonomies[taxonomy["name"]].append(values)
            items = [
                {
                    "title": i["title"],
                    "isbn": i["isbn"],
                    "format": i["format"],
                    "copies": i.get("copies", 1),
                }
                for i in json_data["items"]
            ]
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
    outfile = f"data/new/marc/{today_str}_PROCESSED.mrc"
    set_data = read_app_json()
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
