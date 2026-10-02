import os
from typing import Generator

import pytest
from dotenv import load_dotenv

from mlnyc_records.control_numbers import ControlNumberGenerator


@pytest.fixture
def mock_json(monkeypatch, mock_now) -> None:
    def null_return(*args, **kwargs) -> None:
        pass

    def fake_path_exists(*args, **kwargs) -> str:
        return True

    monkeypatch.setattr("pathlib.Path.exists", fake_path_exists)
    monkeypatch.setattr("pathlib.Path.write_text", null_return)


@pytest.fixture
def mock_ctrl_num_too_high(monkeypatch, mock_json) -> None:
    def fake_read_text(*args, **kwargs) -> str:
        return '{"used_numbers": [3]}'

    monkeypatch.setattr("pathlib.Path.read_text", fake_read_text)


@pytest.fixture
def mock_ctrl_num_too_low(monkeypatch, mock_json) -> None:
    def fake_read_text(*args, **kwargs) -> str:
        return '{"used_numbers": [1]}'

    monkeypatch.setattr("pathlib.Path.read_text", fake_read_text)


class TestControlNumberGenerator:
    def test_control_number_generator(
        self, caplog, mock_ctrl_num_too_high, mock_session
    ):
        with caplog.at_level("DEBUG"):
            generator = ControlNumberGenerator("foo.json")
            assert [i.msg for i in caplog.records] == [
                "Loading current control number data: {'used_numbers': [3]}",
                "Searching Sierra for nn-mlnyc-0000003.",
                "nn-mlnyc-0000003 not found in Sierra.",
                "nn-mlnyc-0000002 found in Sierra.",
                "Next control number is nn-mlnyc-0000003.",
            ]
            assert list(generator.used_numbers) == [2]
            assert generator.next_number == 3

    def test_next_control_number(self, mock_ctrl_num_too_low, mock_session):
        generator = ControlNumberGenerator("foo.json")
        assert generator.next_number == 3
        assert list(generator.used_numbers) == [1, 2]
        control_number = generator.next_control_number()
        assert control_number == "nn-mlnyc-0000003"
        assert list(generator.used_numbers) == [1, 2, 3]
        assert generator.next_number == 4

    def test_next_control_number_no_file(self, caplog):
        generator = ControlNumberGenerator("foo.json")
        control_number = generator.next_control_number()
        assert control_number == "nn-mlnyc-0000001"
        assert caplog.records == []

    def test_save_state_write_to_file(self, mock_ctrl_num_too_low, mock_session):
        generator = ControlNumberGenerator("foo.json")
        control_number = generator.next_control_number()
        assert control_number == "nn-mlnyc-0000003"
        generator.save_state()
        assert list(generator.used_numbers) == [1, 2, 3]
        assert generator.next_number == 4


@pytest.fixture(scope="class")
def live_creds() -> Generator[None, None, None]:
    load_dotenv()
    yield
    os.environ["WORLDCAT_KEY"] = "worldcat_key"
    os.environ["WORLDCAT_SECRET"] = "worldcat_secret"
    os.environ["NYPL_PLATFORM_CLIENT"] = "platform_client"
    os.environ["NYPL_PLATFORM_SECRET"] = "platform_secret"
    os.environ["NYPL_PLATFORM_OAUTH"] = "oauth_server"


class TestControlNumberGeneratorLive:
    @pytest.mark.livetest
    def test_next_control_number_too_high(self, mock_number_too_high, live_creds):
        generator = ControlNumberGenerator("foo.json")
        control_number = generator.next_control_number()
        assert control_number == "nn-mlnyc-0002652"

    @pytest.mark.livetest
    def test_next_control_number_too_low(self, mock_number_too_low, live_creds):
        generator = ControlNumberGenerator("foo.json")
        control_number = generator.next_control_number()
        assert control_number == "nn-mlnyc-0002652"
