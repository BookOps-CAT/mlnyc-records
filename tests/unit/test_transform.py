import pytest

from mlnyc_records.transform import (
    BriefBibResponse,
    FullWorldCatResponse,
    WorldcatManager,
)


class TestWorldcatResponses:
    def test_brief_bib_response(self):
        records = [{"oclcNumber": "ocn777777777"}]
        nums = range(1, 7)
        levels = ["M", "5", "7", "I", " ", "3"]
        records.extend(
            [
                {
                    "oclcNumber": f"ocn{str(i[0]) * 9}",
                    "catalogingInfo": {"levelOfCataloging": i[1]},
                }
                for i in zip(nums, levels)
            ]
        )
        brief_bib_responses = [BriefBibResponse(i) for i in records]
        sorted_responses = sorted(brief_bib_responses, key=BriefBibResponse.sort_key)
        sorted_oclcs = [i.oclc_number for i in sorted_responses]
        sorted_cat_levels = [i.cat_level for i in sorted_responses]
        assert sorted_oclcs == [
            "ocn444444444",
            "ocn555555555",
            "ocn666666666",
            "ocn222222222",
            "ocn333333333",
            "ocn111111111",
            "ocn777777777",
        ]
        assert sorted_cat_levels == ["I", " ", "3", "5", "7", "M", None]
        assert sorted_responses[0].sort_key() == (0, 0)
        assert sorted_responses[1].sort_key() == (0, 0)
        assert sorted_responses[2].sort_key() == (1, 3)
        assert sorted_responses[3].sort_key() == (1, 5)
        assert sorted_responses[4].sort_key() == (1, 7)
        assert sorted_responses[5].sort_key() == (1, 9)
        assert sorted_responses[6].sort_key() == (2, 0)

    def test_full_bib_response(self, stub_bib):
        full_bib_response = FullWorldCatResponse(
            isbn="9781234567897", wc_response=stub_bib
        )
        assert full_bib_response.author_data.format_field() == "Bar, Foo 1980-"
        assert full_bib_response.author_name == "Bar, Foo"
        assert full_bib_response.author_dates == "1980-"
        assert full_bib_response.description == "Fake description of book."
        assert full_bib_response.pub_date == "2000"
        assert full_bib_response.title == "Fake book 1"
        assert list(full_bib_response.to_dict().keys()) == [
            "author_name",
            "author_dates",
            "description",
            "pub_date",
            "title",
            "isbn",
        ]

    def test_full_bib_response_title_part(self, stub_bib):
        stub_bib["245"].add_subfield(code="p", value="Book 2")
        stub_bib["264"].delete_subfield("c")
        stub_bib["264"].add_subfield(code="c", value="2000-2001")
        full_bib_response = FullWorldCatResponse(
            isbn="9781234567897", wc_response=stub_bib
        )
        assert full_bib_response.pub_date == "2000-2001"
        assert full_bib_response.title == "Fake book 1. Book 2"

    def test_full_bib_response_missing_data(self, stub_bib):
        stub_bib.remove_fields("100", "264", "520", "651", "655")
        full_bib_response = FullWorldCatResponse(
            isbn="ocn123456789", wc_response=stub_bib
        )
        assert full_bib_response.author_data is None
        assert full_bib_response.author_name is None
        assert full_bib_response.author_dates is None
        assert full_bib_response.description == ""
        assert full_bib_response.pub_date is None
        assert full_bib_response.title == "Fake book 1"


class TestWorldcatManager:
    def test_get_worldcat_data_for_part(self, mock_session, caplog):
        caplog.set_level("DEBUG")
        with WorldcatManager() as worldcat_manager:
            worldcat_response = worldcat_manager.get_worldcat_data_for_part(
                isbn="9781234567897", index="sn", format=""
            )
        assert worldcat_response["author_name"] == "Bar, Foo"
        assert worldcat_response["author_dates"] == "1980-"
        assert worldcat_response["description"] == "Fake description of book."
        assert worldcat_response["pub_date"] == "2000"
        assert worldcat_response["title"] == "Fake book 1"
        assert list(worldcat_response.keys()) == [
            "author_name",
            "author_dates",
            "description",
            "pub_date",
            "title",
            "isbn",
        ]
        assert [i.msg for i in caplog.records] == [
            "ISBN/UPC `9781234567897`: searching brief bib records.",
            "OCLC number `ocn123456789`: retrieving full bib record.",
        ]

    @pytest.mark.parametrize("format", ["book", "dvd", "lprint", "playaway", "game"])
    def test_get_worldcat_data_for_part_no_records(
        self, mock_session_no_records, format, caplog
    ):
        caplog.set_level("DEBUG")
        with WorldcatManager() as worldcat_manager:
            worldcat_response = worldcat_manager.get_worldcat_data_for_part(
                isbn="9781234567897", index="sn", format=format
            )
        assert worldcat_response["author_name"] is None
        assert worldcat_response["author_dates"] is None
        assert worldcat_response["description"] == ""
        assert worldcat_response["pub_date"] is None
        assert worldcat_response["title"] is None
        assert (
            caplog.records[-1].msg
            == f"No records found in WorldCat for `sn:9781234567897`, `ti:None` and `{format}`."
        )

    @pytest.mark.parametrize("format", ["book", "dvd", "lprint", "playaway", "game"])
    def test_get_worldcat_data_for_part_no_records_title(
        self, mock_session_no_records, format, caplog
    ):
        caplog.set_level("DEBUG")
        with WorldcatManager() as worldcat_manager:
            worldcat_response = worldcat_manager.get_worldcat_data_for_part(
                isbn="9781234567897", index="sn", format=format, title="Foo"
            )
        assert worldcat_response["author_name"] is None
        assert worldcat_response["author_dates"] is None
        assert worldcat_response["description"] == ""
        assert worldcat_response["pub_date"] is None
        assert worldcat_response["title"] == "Foo"
        assert (
            caplog.records[-1].msg
            == f"No records found in WorldCat for `sn:9781234567897`, `ti:Foo` and `{format}`."
        )

    @pytest.mark.parametrize(
        "format,index",
        [
            ("book", " AND x4:PrintBook"),
            ("playaway", " AND x0:AudioBook AND kw:playaway"),
            ("game", ""),
        ],
    )
    def test_get_worldcat_data_for_part_title_search(
        self, mock_session_title_search, format, index, caplog
    ):
        caplog.set_level("DEBUG")
        with WorldcatManager() as worldcat_manager:
            worldcat_response = worldcat_manager.get_worldcat_data_for_part(
                isbn="9781234567890", index="sn", title="Foo", format=format
            )
        assert worldcat_response["author_name"] == "Bar, Foo"
        assert worldcat_response["author_dates"] == "1980-"
        assert worldcat_response["description"] == ""
        assert worldcat_response["pub_date"] == "2000"
        assert worldcat_response["title"] == "Fake book 1"
        assert list(worldcat_response.keys()) == [
            "author_name",
            "author_dates",
            "description",
            "pub_date",
            "title",
            "isbn",
        ]
        assert [i.msg for i in caplog.records] == [
            "ISBN/UPC `9781234567890`: searching brief bib records.",
            f"0 records found for `sn:9781234567890{index}`.",
            "Title `Foo`: searching brief bib records.",
            "OCLC number `ocn123456789`: retrieving full bib record.",
            "Full bib record for `ocn123456789` missing description. Checking next record if present.",
        ]
