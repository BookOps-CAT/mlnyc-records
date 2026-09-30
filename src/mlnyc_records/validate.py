import logging
from typing import Any, Sequence

from pydantic import BaseModel, ConfigDict, model_serializer

logger = logging.getLogger(__name__)


class WorldcatSetPartModel(BaseModel):
    copies: int
    description: str
    isbn: str
    title: str
    author: str | None = None
    author_dates: str | None = None
    format: str | None = "book"
    pub_date: str | None = None

    def entry_dict(self) -> dict[str, Any]:
        subfields = []
        if self.title[-1] not in ["!", "?", ")", "]"]:
            self.title = f"{self.title.strip('.')}."
        if self.author:
            tag = "700"
            ind1 = "1"
            if self.author_dates:
                subfields.append(("a", f"{self.author.strip('.')},"))
                subfields.append(("d", self.author_dates))
                subfields.append(("t", self.title))
            else:
                subfields.append(("a", f"{self.author.strip('.')}."))
                subfields.append(("t", self.title))
        else:
            tag = "730"
            ind1 = "0"
            subfields.append(("a", self.title))
        if self.pub_date:
            self.pub_date = self.pub_date.strip(".")
            if self.pub_date[-1] in ["]", "-"]:
                subfields.append(("f", self.pub_date))
            else:
                subfields.append(("f", f"{self.pub_date}."))
        if self.format == "Large print":
            subfields.append(("s", "Large print edition."))
        subfields.append(("x", self.isbn))
        return {"tag": tag, "ind1": ind1, "ind2": "2", "subfields": subfields}

    def summary_component(self) -> tuple[str, str]:
        return (
            self.title.strip("."),
            self.description.strip("."),
            self.copies,
            self.format,
        )


class SpecialFormatSetPartModel(BaseModel):
    copies: int
    title: str
    description: str = ""
    pub_date: str | None = None

    def entry_dict(self) -> dict[str, Any]:
        return {}

    def summary_component(self) -> tuple[str, str]:
        return (self.title.strip("."), self.description.strip("."), self.copies)


class TeacherSetModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    contents_note: str
    copies_of_set: int
    enhanced: str | None
    grade_level: str
    language: str
    local_genre_term: list[str]
    local_topic_term: list[str]
    parts: Sequence[SpecialFormatSetPartModel | WorldcatSetPartModel]
    physical_description: str
    pub_dates: list[str]
    record_type: str
    set_title: str
    set_type: str
    study_program_info: str

    @model_serializer
    def dump_model(self) -> dict[str, Any]:
        return {
            "added_entries": [i.entry_dict() for i in self.parts if i.entry_dict()],
            "components": [
                i.summary_component() for i in self.parts if i.summary_component()
            ],
            "contents_note": self.contents_note,
            "copies_of_set": self.copies_of_set,
            "grade_level": self.grade_level,
            "enhanced": self.enhanced,
            "language": self.language,
            "local_genre_term": self.local_genre_term,
            "local_topic_term": self.local_topic_term,
            "physical_description": self.physical_description,
            "pub_dates": self.pub_dates,
            "record_type": self.record_type,
            "set_title": self.set_title,
            "set_type": self.set_type,
            "study_program_info": self.study_program_info,
        }
