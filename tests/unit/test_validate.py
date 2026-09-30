import pytest

from mlnyc_records.teacher_sets import SetData, SpecialFormatSetPart, TeacherSet
from mlnyc_records.validate import TeacherSetModel


@pytest.fixture
def stub_set_data(set_test_data) -> TeacherSet:
    return SetData(**set_test_data)


class TestTeacherSetModel:
    def test_teacher_set(self, stub_set_data):
        teacher_set = TeacherSet(
            set_data=stub_set_data,
            worldcat_parts=[
                {
                    "author_name": "Bar, Foo",
                    "author_dates": "1980-",
                    "description": "Fake description of book.",
                    "isbn": "9781234567897",
                    "pub_date": "2000",
                    "title": "Fake book 1",
                    "format": "book",
                    "copies": 2,
                },
                {
                    "description": "",
                    "isbn": "9780987654328",
                    "title": "Fake book 2",
                    "format": "playaway",
                    "copies": 2,
                },
                {
                    "copies": 1,
                    "description": "Another book",
                    "isbn": "9780987654328",
                    "title": "Fake book 3!",
                    "author_name": "Bar, Foo",
                    "format": "lprint",
                    "pub_date": "[2000-2001]",
                },
            ],
        )
        valid_set = TeacherSetModel.model_validate(teacher_set, from_attributes=True)
        assert len(valid_set.parts) == 3
        assert valid_set.parts[0].summary_component() == (
            "Fake book 1",
            "Fake description of book",
            2,
            "book",
        )
        assert valid_set.parts[0].entry_dict() == {
            "tag": "700",
            "ind1": "1",
            "ind2": "2",
            "subfields": [
                ("a", "Bar, Foo,"),
                ("d", "1980-"),
                ("t", "Fake book 1."),
                ("f", "2000."),
                ("x", "9781234567897"),
            ],
        }
        assert valid_set.parts[1].summary_component() == (
            "Fake book 2",
            "",
            2,
            "Playaway audiobook",
        )
        assert valid_set.parts[1].entry_dict() == {
            "tag": "730",
            "ind1": "0",
            "ind2": "2",
            "subfields": [("a", "Fake book 2."), ("x", "9780987654328")],
        }
        assert valid_set.parts[2].summary_component() == (
            "Fake book 3!",
            "Another book",
            1,
            "Large print",
        )
        assert valid_set.parts[2].entry_dict() == {
            "tag": "700",
            "ind1": "1",
            "ind2": "2",
            "subfields": [
                ("a", "Bar, Foo."),
                ("t", "Fake book 3!"),
                ("f", "[2000-2001]"),
                ("s", "Large print edition."),
                ("x", "9780987654328"),
            ],
        }

    def test_teacher_set_special_format(self, stub_set_data, mock_worldcat_response):
        stub_set_data.special_formats = [
            SpecialFormatSetPart(title="Cat puppet", description="A puppet", copies=1)
        ]
        teacher_set = TeacherSet(
            set_data=stub_set_data, worldcat_parts=mock_worldcat_response
        )
        valid_set = TeacherSetModel.model_validate(teacher_set, from_attributes=True)
        special_format = valid_set.parts[-1]
        assert special_format.title == "Cat puppet"
        assert special_format.description == "A puppet"
        assert (
            teacher_set.contents_note
            == 'Set consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2", 1 Cat puppet(s).'
        )
        assert special_format.entry_dict() == {}
        assert special_format.summary_component() == ("Cat puppet", "A puppet", 1)
