import datetime
import logging
from typing import Any

from mlnyc_records.components import (
    BookSetPart,
    DataField,
    FixedField,
    SpecialFormatSetPart,
    WorldcatSetPart,
)
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


class TeacherSetCopy:
    """A bib record for a copy of a MyLibraryNYC TeacherSet."""

    def __init__(
        self,
        added_entries: list[dict[str, Any]],
        components: list[tuple[str, str]],
        contents_note: str,
        copy_number: int,
        grade_level: GradeReadingLevel,
        language: Language,
        physical_description: str,
        pub_dates: list[str],
        record_type: str,
        shelf_number: str,
        study_program_info: SubjectStudyProgram,
        set_title: str,
        set_type: SetTypeFormat,
        copies_of_set: int,
        control_number: str | None = None,
        enhanced: str | None = None,
        local_genre_term: list[str] | None = None,
        local_topic_term: list[str] | None = None,
    ) -> None:
        self.added_entries = added_entries
        self.components = components
        self.contents_note = contents_note
        self.copy_number = copy_number
        self.control_number = control_number
        self.enhanced = enhanced
        self.grade_level = GradeReadingLevel(grade_level)
        self.language = Language(language)
        self.local_genre_term = local_genre_term
        self.local_topic_term = local_topic_term
        self.physical_description = physical_description
        self.pub_dates = pub_dates
        self.record_type = record_type
        self.set_title = set_title
        self.set_type = SetTypeFormat(set_type)
        self.shelf_number = shelf_number
        self.study_program_info = SubjectStudyProgram(study_program_info)
        self.copies_of_set = copies_of_set

    @property
    def leader(self) -> str:
        return f"00000n{self.record_type}c a2200000 a 4500"

    @property
    def field_001(self) -> FixedField:
        """Control number field"""
        return FixedField(tag="001", data=self.control_number)

    @property
    def field_003(self) -> FixedField:
        """Control number identifier field"""
        return FixedField(tag="003", data="BookOps")

    @property
    def field_008(self) -> FixedField:
        """MARC 008 field"""
        lang = self.language.name.lower()
        if lang == "other":
            lang = "|||"
        today = datetime.datetime.strftime(datetime.datetime.today(), "%y%m%d")
        if not self.pub_dates:
            pub_date_str = "nuuuuuuuu"
        else:
            pub_date_str = f"i{self.pub_dates[0]}{self.pub_dates[-1]}"
        date_str = f"{today}{pub_date_str}"
        if self.record_type == "o":
            content = "             | ||"
        else:
            content = "           000 0 "
        return FixedField(tag="008", data=f"{date_str}xxu{content}{lang} d")

    @property
    def field_091(self) -> DataField:
        """Local MyLibraryNYC call number field"""
        if self.enhanced:
            return DataField(
                tag="091",
                indicators=(" ", " "),
                subfields=[
                    ("a", f"MLNYC {self.study_program_info.name}"),
                    ("f", f"{self.set_type.name} {self.enhanced}"),
                    ("p", self.grade_level.name),
                    ("c", self.shelf_number),
                ],
            )
        else:
            return DataField(
                tag="091",
                indicators=(" ", " "),
                subfields=[
                    ("a", f"MLNYC {self.study_program_info.name}"),
                    ("f", self.set_type.name),
                    ("p", self.grade_level.name),
                    ("c", self.shelf_number),
                ],
            )

    @property
    def field_245(self) -> DataField:
        """Title DataField"""
        set_title = self.set_title.strip(" .")
        if set_title[:2] in ["A ", "L'"]:
            ind2 = "2"
        elif set_title[:3] in ["An ", "El ", "La ", "Le "]:
            ind2 = "3"
        elif set_title[:4] in ["The ", "Los ", "Las ", "Les "]:
            ind2 = "4"
        else:
            ind2 = "0"
        if set_title[-1] not in ["!", "?"]:
            set_title = f"{set_title}."
        return DataField(
            tag="245",
            indicators=("0", ind2),
            subfields=[
                ("a", set_title),
                ("p", f"Copy {self.copy_number} of {self.copies_of_set}"),
            ],
        )

    @property
    def field_300(self) -> DataField:
        """Physical description field"""
        return DataField(
            tag="300",
            indicators=(" ", " "),
            subfields=[("a", self.physical_description)],
        )

    @property
    def field_500(self) -> DataField:
        """General contents note field"""
        return DataField(
            tag="500", indicators=(" ", " "), subfields=[("a", self.contents_note)]
        )

    @property
    def field_520(self) -> list[DataField]:
        """Summary description note field (REPEATABLE)"""
        notes = []
        for component in self.components:
            if len(component) > 3 and component[3] in [
                "Large print",
                "Playaway audiobook",
            ]:
                material = f"{component[0]} [{component[3]}]"
            else:
                material = component[0]
            if not component[1]:
                material = f"{material}."
            subfields = [("3", material)]
            if component[1]:
                subfields.append(("a", f"{component[1]}."))
            notes.append(
                DataField(tag="520", indicators=(" ", " "), subfields=subfields)
            )
        return notes

    @property
    def field_521(self) -> DataField:
        """Reading level field"""
        return DataField(
            tag="521", indicators=("2", " "), subfields=[("a", self.grade_level.value)]
        )

    @property
    def field_526(self) -> DataField:
        """Study program information field"""
        subject = self.study_program_info.value.removesuffix(self.language.name).strip()
        return DataField(tag="526", indicators=("8", " "), subfields=[("a", subject)])

    @property
    def field_690(self) -> DataField:
        """Local set type field"""
        return DataField(
            tag="690",
            indicators=(" ", "7"),
            subfields=[("a", f"{self.set_type.value}."), ("2", "bookops")],
        )

    @property
    def field_691(self) -> list[DataField]:
        """Local topic term field (REPEATBLE)"""
        subject_list = []
        if self.local_topic_term:
            for term in self.local_topic_term:
                term = f"{term}."
                subject_list.append(
                    DataField(
                        tag="691",
                        indicators=(" ", "7"),
                        subfields=[("a", term), ("2", "bookops")],
                    )
                )
        return subject_list

    @property
    def field_695(self) -> list[DataField]:
        """Local genre term field (REPEATBLE)"""
        subject_list = []
        if self.local_genre_term:
            for term in self.local_genre_term:
                term = f"{term}."
                subject_list.append(
                    DataField(
                        tag="695",
                        indicators=(" ", "7"),
                        subfields=[("a", term), ("2", "bookops")],
                    )
                )
        return subject_list

    @property
    def field_7xx(self) -> list[DataField]:
        """Author/title/date of publication/ISBN information field (REPEATBLE)"""
        return [
            DataField(
                tag=i["tag"],
                indicators=(i["ind1"], i["ind2"]),
                subfields=[(j[0], j[1]) for j in i["subfields"]],
            )
            for i in self.added_entries
        ]

    @property
    def field_901(self) -> DataField:
        """Cataloger's initials field"""
        return DataField(
            tag="901",
            indicators=(" ", " "),
            subfields=[("a", "mlnyc-bot"), ("b", "CATBL")],
        )

    @property
    def field_909(self) -> DataField:
        """Local OCLC exclusion note field"""
        return DataField(
            tag="909",
            indicators=(" ", " "),
            subfields=[("a", "OCLC Holdings Exclusion")],
        )

    @property
    def field_910(self) -> DataField:
        """Local collection code field"""
        return DataField(tag="910", indicators=(" ", " "), subfields=[("a", "BL")])

    @property
    def command_line_field(self) -> DataField:
        return DataField(
            tag="949", indicators=(" ", " "), subfields=[("a", "*b2=8;b3=e;bn=ed;")]
        )

    @property
    def item_fields(self) -> list[DataField]:
        """Missing: Funding Source"""
        fields = []
        for comp in self.components:
            for copy in range(0, comp[2]):
                if len(comp) < 4 or comp[3] == "book" or comp[3] is None:
                    title = comp[0]
                else:
                    title = f"{comp[0]} [{comp[3]}]"
                fields.append(
                    DataField(
                        tag="949",
                        indicators=(" ", " "),
                        subfields=[
                            ("h", "10"),
                            ("i", f"[BARCODE]-{title}"),
                            ("n", f"{title}"),
                            ("l", "eduls"),
                            ("o", "m"),
                            ("q", "30010"),
                            ("t", "252"),
                            ("u", "-"),
                            ("v", "LOGDOE/mlnyc-bot"),
                        ],
                    )
                )
        return fields

    @property
    def field_list(self) -> list:
        fields = [
            self.field_001,
            self.field_003,
            self.field_008,
            self.field_091,
            self.field_245,
            self.field_300,
            self.field_500,
            self.field_521,
            self.field_526,
            self.field_690,
            self.field_901,
            self.field_909,
            self.field_910,
            self.command_line_field,
        ]
        fields.extend(self.field_520)
        fields.extend(self.field_691)
        fields.extend(self.field_695)
        fields.extend(self.field_7xx)
        fields.extend(self.item_fields)
        return fields
