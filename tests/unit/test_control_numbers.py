from mlnyc_records.control_numbers import ControlNumberGenerator


class TestControlNumberGenerator:
    def test_control_number_generator(self, caplog, mock_control_number_file):
        with caplog.at_level("DEBUG"):
            generator = ControlNumberGenerator("foo.json")
            assert (
                caplog.records[0].msg
                == "Loading current control number data: {'used_numbers': [1]}"
            )
            assert caplog.records[1].msg == "Next control number is 2"
            assert list(generator.used_numbers) == [1]
            assert generator.next_number == 2

    def test_next_control_number(self, mock_control_number_file):
        generator = ControlNumberGenerator("foo.json")
        assert generator.next_number == 2
        assert list(generator.used_numbers) == [1]
        control_number = generator.next_control_number()
        assert control_number == "nn-mlnyc-0000002"
        assert list(generator.used_numbers) == [1, 2]
        assert generator.next_number == 3

    def test_next_control_number_no_file(self, caplog):
        generator = ControlNumberGenerator("foo.json")
        control_number = generator.next_control_number()
        assert control_number == "nn-mlnyc-0000001"
        assert caplog.records == []

    def test_save_state_write_to_file(self, mock_control_number_file):
        generator = ControlNumberGenerator("foo.json")
        control_number = generator.next_control_number()
        assert control_number == "nn-mlnyc-0000002"
        generator.save_state()
        assert list(generator.used_numbers) == [1, 2]
        assert generator.next_number == 3
