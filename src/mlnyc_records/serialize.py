import datetime
import logging
from typing import Any

from pymarc import Field, Indicators, Record, Subfield

from mlnyc_records.taxonomy import (
    GradeReadingLevel,
    Language,
    SetTypeFormat,
    SubjectStudyProgram,
)

logger = logging.getLogger(__name__)


class TeacherSetBib:
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
    def field_001(self) -> Field:
        """Control number field"""
        return Field(tag="001", data=self.control_number)

    @property
    def field_003(self) -> Field:
        """Control number identifier field"""
        return Field(tag="003", data="BookOps")

    @property
    def field_008(self) -> Field:
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
        return Field(tag="008", data=f"{date_str}xxu{content}{lang} d")

    @property
    def field_091(self) -> Field:
        """Local MyLibraryNYC call number field"""
        if self.enhanced:
            return Field(
                tag="091",
                indicators=Indicators(" ", " "),
                subfields=[
                    Subfield(code="a", value=f"MLNYC {self.study_program_info.name}"),
                    Subfield(code="f", value=f"{self.set_type.name} {self.enhanced}"),
                    Subfield(code="p", value=self.grade_level.name),
                    Subfield(code="c", value=self.shelf_number),
                ],
            )
        else:
            return Field(
                tag="091",
                indicators=Indicators(" ", " "),
                subfields=[
                    Subfield(code="a", value=f"MLNYC {self.study_program_info.name}"),
                    Subfield(code="f", value=self.set_type.name),
                    Subfield(code="p", value=self.grade_level.name),
                    Subfield(code="c", value=self.shelf_number),
                ],
            )

    @property
    def field_245(self) -> Field:
        """Title Field"""
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
        return Field(
            tag="245",
            indicators=Indicators("0", ind2),
            subfields=[
                Subfield(code="a", value=set_title),
                Subfield(
                    code="p", value=f"Copy {self.copy_number} of {self.copies_of_set}"
                ),
            ],
        )

    @property
    def field_300(self) -> Field:
        """Physical description field"""
        return Field(
            tag="300",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.physical_description)],
        )

    @property
    def field_500(self) -> Field:
        """General contents note field"""
        return Field(
            tag="500",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=self.contents_note)],
        )

    @property
    def field_520(self) -> list[Field]:
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
            subfields = [Subfield(code="3", value=material)]
            if component[1]:
                subfields.append(Subfield(code="a", value=f"{component[1]}."))
            notes.append(
                Field(tag="520", indicators=Indicators(" ", " "), subfields=subfields)
            )
        return notes

    @property
    def field_521(self) -> Field:
        """Reading level field"""
        return Field(
            tag="521",
            indicators=Indicators("2", " "),
            subfields=[Subfield(code="a", value=self.grade_level.value)],
        )

    @property
    def field_526(self) -> Field:
        """Study program information field"""
        subject = self.study_program_info.value.removesuffix(self.language.name).strip()
        return Field(
            tag="526",
            indicators=Indicators("8", " "),
            subfields=[Subfield(code="a", value=subject)],
        )

    @property
    def field_690(self) -> Field:
        """Local set type field"""
        return Field(
            tag="690",
            indicators=Indicators(" ", "7"),
            subfields=[
                Subfield(code="a", value=f"{self.set_type.value}."),
                Subfield(code="2", value="bookops"),
            ],
        )

    @property
    def field_691(self) -> list[Field]:
        """Local topic term field (REPEATBLE)"""
        subject_list = []
        if self.local_topic_term:
            for term in self.local_topic_term:
                term = f"{term}."
                subject_list.append(
                    Field(
                        tag="691",
                        indicators=Indicators(" ", "7"),
                        subfields=[
                            Subfield(code="a", value=term),
                            Subfield(code="2", value="bookops"),
                        ],
                    )
                )
        return subject_list

    @property
    def field_695(self) -> list[Field]:
        """Local genre term field (REPEATBLE)"""
        subject_list = []
        if self.local_genre_term:
            for term in self.local_genre_term:
                term = f"{term}."
                subject_list.append(
                    Field(
                        tag="695",
                        indicators=Indicators(" ", "7"),
                        subfields=[
                            Subfield(code="a", value=term),
                            Subfield(code="2", value="bookops"),
                        ],
                    )
                )
        return subject_list

    @property
    def field_7xx(self) -> list[Field]:
        """Author/title/date of publication/ISBN information field (REPEATBLE)"""
        return [
            Field(
                tag=i["tag"],
                indicators=Indicators(i["ind1"], i["ind2"]),
                subfields=[Subfield(code=j[0], value=j[1]) for j in i["subfields"]],
            )
            for i in self.added_entries
        ]

    @property
    def field_901(self) -> Field:
        """Cataloger's initials field"""
        return Field(
            tag="901",
            indicators=Indicators(" ", " "),
            subfields=[
                Subfield(code="a", value="mlnyc-bot"),
                Subfield(code="b", value="CATBL"),
            ],
        )

    @property
    def field_909(self) -> Field:
        """Local OCLC exclusion note field"""
        return Field(
            tag="909",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="OCLC Holdings Exclusion")],
        )

    @property
    def field_910(self) -> Field:
        """Local collection code field"""
        return Field(
            tag="910",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="BL")],
        )

    @property
    def command_line_field(self) -> Field:
        return Field(
            tag="949",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="*b2=8;b3=e;bn=ed;")],
        )

    @property
    def item_fields(self) -> list[Field]:
        """Missing: Funding Source"""
        fields = []
        for comp in self.components:
            for copy in range(0, comp[2]):
                if len(comp) < 4 or comp[3] == "book" or comp[3] is None:
                    title = comp[0]
                else:
                    title = f"{comp[0]} [{comp[3]}]"
                fields.append(
                    Field(
                        tag="949",
                        indicators=Indicators(" ", " "),
                        subfields=[
                            Subfield(code="h", value="10"),
                            Subfield(code="i", value=f"[BARCODE]-{title}"),
                            Subfield(code="n", value=f"{title}"),
                            Subfield(code="l", value="eduls"),
                            Subfield(code="o", value="m"),
                            Subfield(code="q", value="30010"),
                            Subfield(code="t", value="252"),
                            Subfield(code="u", value="-"),
                            Subfield(code="v", value="LOGDOE/mlnyc-bot"),
                        ],
                    )
                )
        return fields

    def to_bib(self) -> Record:
        bib = Record()
        bib.leader = f"00000n{self.record_type}c a2200000 a 4500"
        bib.add_ordered_field(self.field_001)
        bib.add_ordered_field(self.field_003)
        bib.add_ordered_field(self.field_008)
        bib.add_ordered_field(self.field_091)
        bib.add_ordered_field(self.field_245)
        bib.add_ordered_field(self.field_300)
        bib.add_ordered_field(self.field_500)
        for field in self.field_520:
            bib.add_ordered_field(field)
        bib.add_ordered_field(self.field_521)
        bib.add_ordered_field(self.field_526)
        bib.add_ordered_field(self.field_690)
        for field in self.field_691:
            bib.add_ordered_field(field)
        for field in self.field_695:
            bib.add_ordered_field(field)
        for field in self.field_7xx:
            bib.add_ordered_field(field)
        bib.add_ordered_field(self.field_901)
        bib.add_ordered_field(self.field_909)
        bib.add_ordered_field(self.field_910)
        bib.add_ordered_field(self.command_line_field)
        for field in self.item_fields:
            bib.add_ordered_field(field)
        return bib
