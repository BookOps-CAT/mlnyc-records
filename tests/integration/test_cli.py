from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from mlnyc_records import main, mlnyc_records


@pytest.fixture
def mock_json_data(mocker) -> None:
    data = b'{"curation_list_name": "Foo: Bar","copies_to_procure": 5,"taxonomies": [{"name": "genre", "values": "Comics & Graphic Novels"}, {"name": "grade", "values": "3-5"}, {"name": "language", "values": "English"}, {"name": "set_type", "values": "Book Club"}, {"name": "subject", "values": "Language Arts"}, {"name": "topic", "values": ["Concepts", "Ancient Civilization"]}],"item_count": 1,"items": [{"position": 1, "title": "Foo: Bar", "isbn": "9781338801910", "format": "book", "formatLabel": "Book", "copies": 10}]}'

    mock_read = mocker.mock_open(read_data=data)
    mock_write = mocker.mock_open()
    mocker.patch("mlnyc_records.commands.open", mock_read)
    mocker.patch("mlnyc_records.build.open", mock_write)


@pytest.fixture
def mock_read_app_json(monkeypatch, mock_json_data) -> None:
    def mock_iterdir(*args, **kwargs) -> list:
        return [Path("foo")]

    def mock_is_file(*args, **kwargs) -> bool:
        return True

    monkeypatch.setattr(Path, "iterdir", mock_iterdir)
    monkeypatch.setattr(Path, "is_file", mock_is_file)


@pytest.fixture
def cli_runner(
    monkeypatch, mock_session, mock_control_number_file, mock_read_app_json
) -> CliRunner:
    runner = CliRunner()
    monkeypatch.setattr("logging.config.dictConfig", lambda *args, **kwargs: None)
    return runner


@pytest.fixture
def mock_invalid_set(monkeypatch) -> None:
    def mock_worldcat_data(*args, **kwargs) -> dict[str, Any]:
        return [
            {
                "author_name": None,
                "author_dates": None,
                "description": "",
                "isbn": "9781234567897",
                "pub_date": None,
                "title": "Fake book 1",
                "format": 1,
                "copies": 2,
            }
        ]

    monkeypatch.setattr(
        "mlnyc_records.teacher_sets.SetData.get_worldcat_data_for_items",
        mock_worldcat_data,
    )


class TestCLI:
    def test_main(self, mocker):
        mock_main = mocker.Mock()
        mocker.patch("mlnyc_records.main", return_value=mock_main)
        with pytest.raises(SystemExit):
            main()

    def test_mlnyc_records(self):
        runner = CliRunner()
        runner.invoke(mlnyc_records)
        assert runner.get_default_prog_name(mlnyc_records) == "mlnyc-records"

    def test_mlnyc_records_build(self, cli_runner, caplog):
        result = cli_runner.invoke(cli=mlnyc_records, args=["build"])
        assert result.exit_code == 0
        assert [i.msg for i in caplog.records] == [
            "Next control number is nn-mlnyc-0000003.",
            "Building teacher set from new data: 'Foo: Bar'.",
            "(nn-mlnyc-0000003) Created 5 valid copy/copies of set.",
            "(nn-mlnyc-0000003) Writing records to file for set.",
        ]

    def test_mlnyc_records_build_debug(self, cli_runner, caplog):
        caplog.set_level("DEBUG")
        result = cli_runner.invoke(cli=mlnyc_records, args=["build"])
        assert result.exit_code == 0
        assert [i.msg for i in caplog.records] == [
            "Loading current control number data: {'used_numbers': [1]}",
            "Searching Sierra for nn-mlnyc-0000001.",
            "nn-mlnyc-0000001 found in Sierra.",
            "nn-mlnyc-0000002 found in Sierra.",
            "nn-mlnyc-0000003 not found in Sierra.",
            "Next control number is nn-mlnyc-0000003.",
            "Building teacher set from new data: 'Foo: Bar'.",
            "ISBN/UPC `9781338801910`: searching brief bib records.",
            "OCLC number `ocn123456789`: retrieving full bib record.",
            "(nn-mlnyc-0000003) Creating 5 copy/copies of set.",
            "(nn-mlnyc-0000003) Created 5 valid copy/copies of set.",
            "(nn-mlnyc-0000003) Writing records to file for set.",
        ]

    def test_build_teacher_validation_error(self, cli_runner, mock_invalid_set, caplog):
        result = cli_runner.invoke(cli=mlnyc_records, args=["build"])
        assert result.exit_code == 0
        assert len(caplog.records) == 3
        assert caplog.records[0].msg == "Next control number is nn-mlnyc-0000003."
        assert (
            caplog.records[1].msg == "Building teacher set from new data: 'Foo: Bar'."
        )
        assert caplog.records[2].msg.startswith("Validation errors for set: ") is True
