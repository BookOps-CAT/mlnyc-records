import copy

import pytest

from mlnyc_records.taxonomy import (
    GradeReadingLevel,
    Language,
    SetTypeFormat,
    SubjectStudyProgram,
    TaxonomyGenre,
    TaxonomyTopic,
)
from mlnyc_records.teacher_sets import SetData, TeacherSet


class TestSetData:
    def test_set_data(self, set_test_data):
        set_data = SetData(**set_test_data)
        assert set_data.grade_level == GradeReadingLevel.A
        assert set_data.language == Language.ENG
        assert set_data.local_topic_term == [TaxonomyTopic.new_york_city]
        assert set_data.local_genre_term == [TaxonomyGenre.fiction]
        assert set_data.items[0].isbn == "9781234567897"
        assert len(set_data.items) == 2
        assert set_data.record_type == "a"
        assert set_data.set_title == "Foo Bar Teacher Set"
        assert set_data.set_type == SetTypeFormat.CLUB
        assert set_data.study_program_info == SubjectStudyProgram.SOC

    def test_set_data_special_format(self, set_test_data):
        set_test_data["special_formats"] = [
            {"title": "Cat puppet", "description": "A puppet", "copies": 1}
        ]
        set_data = SetData(**set_test_data)
        assert set_data.enhanced == "E"
        assert set_data.record_type == "o"

    @pytest.mark.parametrize(
        "in_lang,out_lang,study_program_info",
        [
            ("English", Language.ENG, SubjectStudyProgram.ELA),
            ("Chinese", Language.CHI, SubjectStudyProgram.CHLA),
            ("French", Language.FRE, SubjectStudyProgram.FRLA),
            ("Spanish", Language.SPA, SubjectStudyProgram.SPLA),
            ("Other", Language.OTHER, SubjectStudyProgram.WorldLang),
        ],
    )
    def test_set_data_languages(
        self, set_test_data, in_lang, out_lang, study_program_info
    ):
        set_data = copy.deepcopy(set_test_data)
        set_data["language"] = in_lang
        set_data["subject"] = "Language Arts"
        set_data = SetData(**set_data)
        assert set_data.language == out_lang
        assert set_data.study_program_info == study_program_info

    @pytest.mark.parametrize(
        "arg,output",
        [
            ("978-0-78-930884-9 ", "9780789308849"),
            (" 068816241X. ", "068816241X"),
            ("816069239", "0816069239"),
        ],
    )
    def test_set_data_validate_ids(self, set_test_data, arg, output):
        set_test_data["items"][0]["isbn"] = arg
        set_data = SetData(**set_test_data)
        assert set_data.items[0].isbn == output

    @pytest.mark.parametrize(
        "isbn", ["asdfgh", "978078930884X", "97897897X9", "078930884Z", "012345678906"]
    )
    def test_set_data_invalid_ids(self, set_test_data, isbn):
        set_test_data["items"][0]["isbn"] = isbn
        with pytest.raises(ValueError) as exc:
            SetData(**set_test_data)
        assert str(exc.value) == f"ISBN/UPC is invalid: {isbn}."

    def test_set_data_get_parts(self, set_test_data, mock_session):
        set_data = SetData(**set_test_data)
        worldcat_parts = set_data.get_worldcat_data_for_items()
        assert len(worldcat_parts) == 2
        assert worldcat_parts[0]["author_name"] == "Bar, Foo"
        assert worldcat_parts[0]["author_dates"] == "1980-"
        assert worldcat_parts[0]["description"] == "Fake description of book."
        assert worldcat_parts[0]["pub_date"] == "2000"
        assert worldcat_parts[0]["title"] == "Fake book 1"


class TestTeacherSet:
    def test_teacher_set(self, set_test_data, mock_worldcat_response):
        set_data = SetData(**set_test_data)
        teacher_set = TeacherSet(
            set_data=set_data, worldcat_parts=mock_worldcat_response
        )
        assert len(teacher_set.parts) == 2
        assert teacher_set.parts[0].author == "Bar, Foo"
        assert teacher_set.parts[0].author_dates == "1980-"
        assert teacher_set.parts[0].description == "Fake description of book."
        assert teacher_set.parts[0].pub_date == "2000"
        assert teacher_set.physical_description == "4 item(s)"
        assert (
            teacher_set.contents_note
            == 'Set consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2".'
        )
        assert teacher_set.pub_dates == ["2000"]

    def test_teacher_set_special_format(self, set_test_data, mock_worldcat_response):
        set_test_data["special_formats"] = [
            {"title": "Cat puppet", "description": "A puppet", "copies": 1}
        ]
        set_data = SetData(**set_test_data)
        teacher_set = TeacherSet(
            set_data=set_data, worldcat_parts=mock_worldcat_response
        )
        special_format = teacher_set.parts[-1]
        assert special_format.title == "Cat puppet"
        assert special_format.description == "A puppet"
        assert (
            teacher_set.contents_note
            == 'Set consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2", 1 Cat puppet(s).'
        )

    def test_teacher_set_single_copy(self, set_test_data, mock_worldcat_response):
        mock_worldcat_response[0]["copies"] = 1
        mock_worldcat_response[1]["copies"] = 1
        set_test_data["items"][0]["copies"] = 1
        set_test_data["items"][1]["copies"] = 1
        set_data = SetData(**set_test_data)
        teacher_set = TeacherSet(
            set_data=set_data, worldcat_parts=mock_worldcat_response
        )
        assert teacher_set.physical_description == "2 item(s)"
        assert (
            teacher_set.contents_note
            == 'Set consists of 1 copy of "Fake book 1", 1 copy of "Fake book 2".'
        )

    @pytest.mark.parametrize(
        "date1,date2,output",
        [
            (None, None, []),
            ("2000", "2020", ["2000", "2020"]),
            ("2000", "202u", ["2000"]),
            ("20uu", "20uu", ["20uu", "20uu"]),
        ],
    )
    def test_teacher_set_pub_dates(
        self, set_test_data, mock_worldcat_response, date1, date2, output
    ):
        mock_worldcat_response[0]["pub_date"] = date1
        mock_worldcat_response[1]["pub_date"] = date2
        set_data = SetData(**set_test_data)
        teacher_set = TeacherSet(
            set_data=set_data, worldcat_parts=mock_worldcat_response
        )
        assert teacher_set.pub_dates == output
