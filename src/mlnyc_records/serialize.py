import logging

from pymarc import Field, Indicators, Record, Subfield

logger = logging.getLogger(__name__)


class TeacherSetBib:
    """A bib record for a copy of a MyLibraryNYC TeacherSet."""

    def __init__(self, control_number: str, field_list: list, leader: str) -> None:
        self.control_number = control_number
        self.field_list = field_list
        self.leader = leader

    @property
    def fields(self) -> list[Field]:
        fields = []
        for field in self.field_list:
            if hasattr(field, "data"):
                fields.append(Field(tag=field.tag, data=field.data))
            else:
                fields.append(
                    Field(
                        tag=field.tag,
                        indicators=Indicators(field.indicators[0], field.indicators[1]),
                        subfields=[
                            Subfield(code=i[0], value=i[1]) for i in field.subfields
                        ],
                    )
                )
        return fields

    def to_bib(self) -> Record:
        bib = Record()
        bib.leader = self.leader
        for field in self.fields:
            bib.add_ordered_field(field)
        return bib
