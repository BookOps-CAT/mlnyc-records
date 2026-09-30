import logging
from typing import Any

from mlnyc_records.components import BookSetPart, SpecialFormatSetPart, WorldcatSetPart
from mlnyc_records.taxonomy import (
    ComponentFormat,
    GradeReadingLevel,
    Language,
    SetTypeFormat,
    SubjectStudyProgram,
    TaxonomyGenre,
    TaxonomyTopic,
)
from mlnyc_records.transform import WorldcatManager

logger = logging.getLogger(__name__)


class SetData:
    """A data model for a copy of a MyLibraryNYC TeacherSet."""

    def __init__(
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
    ) -> None:
        self.copies_of_set = copies_of_set
        self.grade_level = GradeReadingLevel(grade_level)
        self.language = Language(language)
        self.local_genre_term: list[TaxonomyGenre] = (
            [TaxonomyGenre(i) for i in local_genre_term] if local_genre_term else []
        )
        self.local_topic_term: list[TaxonomyTopic] = (
            [TaxonomyTopic(i) for i in local_topic_term] if local_topic_term else []
        )

        self.items = [BookSetPart(**i) for i in items]
        self.set_title = set_title
        self.set_type = SetTypeFormat(set_type)
        self.subject = subject
        self.special_formats = (
            [SpecialFormatSetPart(**i) for i in special_formats]
            if special_formats
            else None
        )

    @property
    def enhanced(self) -> str | None:
        if self.special_formats:
            return "E"
        return None

    @property
    def record_type(self) -> str:
        if self.enhanced:
            return "o"
        return "a"

    @property
    def study_program_info(self) -> SubjectStudyProgram:
        lang_stub = self.language.name
        lang_list = ["CHI", "ENG", "FRE", "SPA"]
        if self.subject == "Language Arts" and self.language.name in lang_list:
            return SubjectStudyProgram(f"{self.subject} {lang_stub}")
        return SubjectStudyProgram(self.subject)

    def get_worldcat_data_for_items(self) -> list[dict[str, Any]]:
        items = []
        with WorldcatManager() as manager:
            for item in self.items:
                worldcat_part = manager.get_worldcat_data_for_part(
                    isbn=item.isbn, index="sn", format=item.format, title=item.title
                )
                worldcat_part.update(
                    {"isbn": item.isbn, "format": item.format, "copies": item.copies}
                )
                items.append(worldcat_part)
        return items


class TeacherSet:
    def __init__(self, set_data: SetData, worldcat_parts: list[dict[str, Any]]) -> None:
        self._set_data = set_data

        self.copies_of_set = self._set_data.copies_of_set
        self.enhanced = self._set_data.enhanced
        self.grade_level = self._set_data.grade_level
        self.language = self._set_data.language
        self.local_genre_term = self._set_data.local_genre_term
        self.local_topic_term = self._set_data.local_topic_term
        self.record_type = self._set_data.record_type
        self.set_title = self._set_data.set_title
        self.set_type = self._set_data.set_type
        self.study_program_info = self._set_data.study_program_info
        self.worldcat_parts = worldcat_parts

    @property
    def contents_note(self) -> str:
        part_list = []
        special_formats = []
        for part in self.parts:
            copies = str(part.copies)
            title = part.title.strip(".")
            if isinstance(part, SpecialFormatSetPart):
                special_formats.append("".join([copies, f" {title}(s), "]))
            elif part.copies > 1:
                part_list.append("".join([copies, ' copies of "', title, '", ']))
            else:
                part_list.append("".join([copies, ' copy of "', title, '", ']))
        if self._set_data.special_formats:
            part_list.extend(special_formats)
        return f"Set consists of {''.join(part_list).rstrip(', ')}."

    @property
    def parts(self) -> list[WorldcatSetPart]:
        parts = []
        for worldcat_part in self.worldcat_parts:
            parts.append(
                WorldcatSetPart(
                    isbn=worldcat_part["isbn"],
                    title=worldcat_part["title"],
                    author=worldcat_part.get("author_name"),
                    author_dates=worldcat_part.get("author_dates"),
                    pub_date=worldcat_part.get("pub_date"),
                    description=worldcat_part["description"],
                    copies=worldcat_part["copies"],
                    format=ComponentFormat[worldcat_part["format"]],
                )
            )
        if self._set_data.special_formats:
            parts.extend(self._set_data.special_formats)
        return parts

    @property
    def physical_description(self) -> str:
        return f"{sum([i.copies for i in self.parts])} item(s)"

    @property
    def pub_dates(self) -> list[str]:
        all_pub_dates = []
        fuzzy_dates = []
        for part in self.parts:
            date = part.pub_date
            if isinstance(date, str) and date.isdigit():
                all_pub_dates.append(date)
            elif isinstance(date, str) and date.isalnum():
                fuzzy_dates.append(date)
        if all_pub_dates:
            return sorted([str(i) for i in all_pub_dates])
        elif fuzzy_dates:
            return sorted(fuzzy_dates)
        return all_pub_dates
