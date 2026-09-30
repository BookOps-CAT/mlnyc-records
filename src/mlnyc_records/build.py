import copy
import logging
from typing import Any

from mlnyc_records.control_numbers import ControlNumberGenerator
from mlnyc_records.serialize import TeacherSetBib
from mlnyc_records.teacher_sets import SetData, TeacherSet, TeacherSetCopy
from mlnyc_records.validate import TeacherSetModel

logger = logging.getLogger(__name__)


class TeacherSetBuilder:
    def __init__(self, file: str | None = "data/control_number_state.json") -> None:
        self.ctrl_number_gen = ControlNumberGenerator(file)

    def build_teacher_set(
        self,
        copies_of_set: int,
        grade_level: str,
        language: str,
        items: list[dict[str, str]],
        set_title: str,
        set_type: str,
        subject: str,
        local_genre_term: list[str] | None = None,
        local_topic_term: list[str] | None = None,
        special_formats: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        logger.info(f"Building teacher set from new data: '{set_title}'.")
        set_data = SetData(
            copies_of_set=copies_of_set,
            grade_level=grade_level,
            language=language,
            items=items,
            set_title=set_title,
            set_type=set_type,
            subject=subject,
            local_genre_term=local_genre_term,
            local_topic_term=local_topic_term,
            special_formats=special_formats,
        )
        worldcat_parts = set_data.get_worldcat_data_for_items()
        teacher_set = TeacherSet(set_data=set_data, worldcat_parts=worldcat_parts)
        valid_set = TeacherSetModel.model_validate(teacher_set, from_attributes=True)
        return valid_set.model_dump()

    def build_set_copies(
        self, set_data: dict[str, Any], control_number: str
    ) -> list[TeacherSetBib]:
        copies = set_data["copies_of_set"]
        logger.debug(f"({control_number}) Creating {copies} copy/copies of set.")
        valid = []
        set_data["control_number"] = control_number
        for copy_num in range(0, copies):
            set_copy_dict = copy.deepcopy(set_data)
            set_copy_dict["shelf_number"] = "[SHELF-NUMBER]"
            set_copy_dict["copy_number"] = copy_num + 1
            set_copy = TeacherSetCopy(**set_copy_dict)
            set_bib = TeacherSetBib(
                control_number=set_copy.control_number,
                field_list=set_copy.field_list,
                leader=set_copy.leader,
            )
            valid.append(set_bib)
        logger.info(
            f"({control_number}) Created {len(valid)} valid copy/copies of set."
        )
        return valid

    def write_marc_to_file(self, out_file: str, set_bibs: list[TeacherSetBib]) -> None:
        logger.info(f"({set_bibs[0].control_number}) Writing records to file for set.")
        with open(out_file, "ab") as fh:
            for set_bib in set_bibs:
                bib = set_bib.to_bib()
                fh.write(bib.as_marc())
