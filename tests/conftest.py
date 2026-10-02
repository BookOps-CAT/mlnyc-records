import datetime
import logging
import os
from pathlib import Path
from typing import Any

import pytest
from bookops_nypl_platform import PlatformSession, PlatformToken
from bookops_worldcat import MetadataSession, WorldcatAccessToken
from pymarc import Field, Indicators, Record, Subfield

from mlnyc_records.teacher_sets import SetData, TeacherSet


@pytest.fixture
def mock_creds() -> None:
    os.environ["NYPL_PLATFORM_CLIENT"] = "platform_client"
    os.environ["NYPL_PLATFORM_SECRET"] = "platform_secret"
    os.environ["NYPL_PLATFORM_OAUTH"] = "oauth_server"
    os.environ["WORLDCAT_KEY"] = "worldcat_key"
    os.environ["WORLDCAT_SECRET"] = "worldcat_secret"


@pytest.fixture(autouse=True)
def setup_logging(caplog) -> None:
    caplog.set_level(logging.INFO)


class MockDatetimeNow(datetime.datetime):
    @classmethod
    def today(cls, tzinfo=datetime.timezone.utc) -> "MockDatetimeNow":
        return cls(2000, 1, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)


@pytest.fixture(autouse=True)
def mock_now(monkeypatch) -> None:
    monkeypatch.setattr(datetime, "datetime", MockDatetimeNow)


@pytest.fixture
def set_test_data() -> dict[str, Any]:
    return {
        "copies_of_set": 2,
        "grade_level": "Pre-K",
        "language": "English",
        "set_title": "Foo Bar Teacher Set",
        "items": [
            {"isbn": "9781234567897", "copies": 2, "format": "book"},
            {"copies": 2, "isbn": "9780987654328", "format": "book"},
        ],
        "set_type": "Book Club",
        "subject": "Social Studies",
        "local_genre_term": ["Fiction"],
        "local_topic_term": ["New York City"],
    }


@pytest.fixture
def stub_teacher_set(mock_worldcat_response, set_test_data) -> TeacherSet:
    set_data = SetData(**set_test_data)
    return TeacherSet(set_data=set_data, worldcat_parts=mock_worldcat_response)


@pytest.fixture
def stub_bib_data() -> dict:
    return {
        "added_entries": [
            {
                "tag": "730",
                "ind1": "0",
                "ind2": "2",
                "subfields": [("a", "Fake book 1."), ("x", "9781234567897")],
            }
        ],
        "components": [("Fake book 1", "", 2, "book")],
        "contents_note": 'Set consists of 2 copies of "Fake book 1".',
        "control_number": "nn-mlnyc-0000001",
        "copies_of_set": 2,
        "copy_number": 1,
        "grade_level": "Pre-K",
        "enhanced": None,
        "language": "English",
        "local_genre_term": [],
        "local_topic_term": [],
        "physical_description": "2 item(s)",
        "pub_dates": [],
        "record_type": "a",
        "set_title": "Foo Bar Teacher Set",
        "set_type": "Book Club",
        "shelf_number": "[SHELF-NUMBER]",
        "study_program_info": "Social Studies",
    }


@pytest.fixture
def stub_bib() -> Record:
    record = Record()
    record.add_field(
        Field(
            tag="100",
            indicators=Indicators("1", " "),
            subfields=[
                Subfield(code="a", value="Bar, Foo"),
                Subfield(code="d", value="1980-"),
            ],
        )
    )
    record.add_field(
        Field(
            tag="245",
            indicators=Indicators("0", "0"),
            subfields=[Subfield(code="a", value="Fake book 1.")],
        )
    )
    record.add_field(
        Field(
            tag="264",
            indicators=Indicators(" ", "1"),
            subfields=[
                Subfield(code="a", value="New York :"),
                Subfield(code="b", value="Universe,"),
                Subfield(code="c", value="2000."),
            ],
        )
    )
    record.add_field(
        Field(
            tag="520",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="Fake description of book.")],
        )
    )
    record.add_field(
        Field(
            tag="650",
            indicators=Indicators(" ", "7"),
            subfields=[
                Subfield(code="a", value="Fake fast term."),
                Subfield(code="2", value="fast"),
            ],
        )
    )
    record.add_field(
        Field(
            tag="650",
            indicators=Indicators(" ", "4"),
            subfields=[Subfield(code="a", value="NYC")],
        )
    )
    record.add_field(
        Field(
            tag="651",
            indicators=Indicators(" ", "0"),
            subfields=[Subfield(code="a", value="New York (N.Y.)")],
        )
    )
    record.add_field(
        Field(
            tag="655",
            indicators=Indicators(" ", "7"),
            subfields=[
                Subfield(code="a", value="Comics (Graphic works)."),
                Subfield(code="2", value="lcgft"),
            ],
        )
    )
    return record


@pytest.fixture()
def mock_worldcat_response() -> list[dict[str, Any]]:
    return [
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
            "author_name": None,
            "author_dates": None,
            "description": "Another fake description of a book.",
            "isbn": "9780987654328",
            "pub_date": "20uu",
            "title": "Fake book 2",
            "format": "book",
            "copies": 2,
        },
    ]


class MockHTTPResponse:
    def __init__(self, _json: dict | None = None, _content: bytes | None = None):
        self._json = _json
        self._content = _content

    @property
    def content(self):
        return self._content

    def json(self):
        return self._json


@pytest.fixture
def mock_session(monkeypatch, stub_bib, mock_creds) -> None:
    def get_worldcat_bib(*args, **kwargs):
        return MockHTTPResponse(_content=stub_bib.as_marc())

    def get_worldcat_brief_bib(*args, **kwargs):
        return MockHTTPResponse(
            _json={
                "briefRecords": [
                    {
                        "oclcNumber": "ocn123456789",
                        "catalogingInfo": {"levelOfCataloging": " "},
                    }
                ]
            }
        )

    def fake_token(*args, **kwargs) -> None:
        pass

    def search_platform_bibs(*args, **kwargs):
        ctrl_num = args[1]
        if ctrl_num in ["nn-mlnyc-0000001", "nn-mlnyc-0000002"]:
            return MockHTTPResponse({"data": [{"id": "1"}]})
        else:
            return MockHTTPResponse({"data": []})

    monkeypatch.setattr(PlatformToken, "_get_token", fake_token)
    monkeypatch.setattr(PlatformSession, "_update_authorization", fake_token)
    monkeypatch.setattr(PlatformSession, "search_controlNos", search_platform_bibs)
    monkeypatch.setattr(WorldcatAccessToken, "_request_token", fake_token)
    monkeypatch.setattr(MetadataSession, "brief_bibs_search", get_worldcat_brief_bib)
    monkeypatch.setattr(MetadataSession, "bib_get", get_worldcat_bib)


@pytest.fixture
def mock_session_no_records(monkeypatch, mock_session) -> None:
    def get_worldcat_brief_bib(*args, **kwargs):
        return MockHTTPResponse(_json={"briefRecords": []})

    monkeypatch.setattr(MetadataSession, "brief_bibs_search", get_worldcat_brief_bib)


@pytest.fixture
def mock_session_title_search(monkeypatch, mock_session, stub_bib) -> None:
    def get_worldcat_brief_bib(*args, **kwargs):
        query = kwargs.get("q")
        if "ti:" not in query:
            return MockHTTPResponse(_json={"briefRecords": []})
        return MockHTTPResponse(
            _json={
                "briefRecords": [
                    {
                        "oclcNumber": "ocn123456789",
                        "catalogingInfo": {"levelOfCataloging": " "},
                    }
                ]
            }
        )

    def get_worldcat_bib_no_description(*args, **kwargs):
        bib = stub_bib
        bib.remove_fields("520")
        return MockHTTPResponse(_content=bib.as_marc())

    monkeypatch.setattr(MetadataSession, "bib_get", get_worldcat_bib_no_description)
    monkeypatch.setattr(MetadataSession, "brief_bibs_search", get_worldcat_brief_bib)


@pytest.fixture
def mock_control_number_file(monkeypatch, mock_now) -> None:
    def null_return(*args, **kwargs) -> None:
        pass

    def fake_read_text(*args, **kwargs) -> str:
        return '{"used_numbers": [1]}'

    def fake_path_exists(*args, **kwargs) -> str:
        return True

    monkeypatch.setattr(Path, "exists", fake_path_exists)
    monkeypatch.setattr(Path, "read_text", fake_read_text)
    monkeypatch.setattr(Path, "write_text", null_return)
