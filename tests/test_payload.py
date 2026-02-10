from scripts.payload import Message, POWER_FACTOR, VOLTS
import pytest

_TRANSMITTER_PACKET = "5555553475c58c0000800d000027b10000008e01000e240"
_SEARCH_MODE_PACKET= "5555553475c58cffff100d000000000000000000006fd80"
_CORRUPTED_SYNCWORD_PACKET= "5555559999c58c0000800d000027b10000008e01000e240"
_CORRUPTED_CRC_PACKET= "5555553475c58c0000800d000027b10000008e0100123450"
_CORRUPTED_DATA_PACKET = "5555553475c58c0000800d000027b10000009e01000e240"
_MISSING_PREAMBLE_PACKET= "3475c58c0000800d000027b10000008e01000e240"
_MAX_TOTAL_AH_PACKET= "5555553475c58c0000800d00ffffff00000000010003af20"
_MAX_CURRENT_A_PACKET= "5555553475c58c0000800d000000000000ffff0100f8a30"
_ZERO_VALUES_PACKET = "5555553475c58c0000800d000000000000000000006fd80"
_CRC_LEFT_SHIFT_PACKET = "5555553475c58c0000800d000027b10000008e010007120"
_CRC_RIGHT_SHIFT_PACKET = "5555553475c58c0000800d000027b10000008e01001c480"


class TestMessageFromStr:
    @pytest.mark.parametrize("input_string", [
        _TRANSMITTER_PACKET,
        _SEARCH_MODE_PACKET
    ])
    def test_from_str_transmitter_packet(self, input_string):
        msg = Message.from_str(input_string)
        assert msg is not None, f"Failed to parse valid input string: {input_string}"
        assert msg.raw == input_string, f"Failed to preserve input string: {input_string}"
        
    def test_field_extraction_receiver_id(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        assert msg.receiver_id == "c58c"
        
    def test_field_extraction_sender_id_transmitter(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        assert msg.sender_id == "0000"
        
    def test_field_extraction_sender_id_search_mode(self):
        msg = Message.from_str(_SEARCH_MODE_PACKET)
        assert msg.sender_id == "ffff"
        
    def test_field_extraction_u1_transmitter(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        assert msg.u1 == "80"
        
    def test_field_extraction_u1_search_mode(self):
        msg = Message.from_str(_SEARCH_MODE_PACKET)
        assert msg.u1 == "10"
        
    def test_field_extraction_u2(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        assert msg.u2 == "0d"
        
    def test_field_extraction_u3(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        assert msg.u3 == "00"
        
    def test_total_ah_calculation_transmitter(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        assert msg.total_Ah == pytest.approx(101.61)
        assert msg.raw_total_Ah == "0027b1"
        
    def test_total_ah_calculation_search_mode(self):
        msg = Message.from_str(_SEARCH_MODE_PACKET)
        assert msg.total_Ah == pytest.approx(0.0)
        assert msg.raw_total_Ah == "000000"
        
    def test_current_a_calculation_transmitter(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        assert msg.current_A == pytest.approx(1.42)
        assert msg.raw_current_A == "008e"
        
    def test_current_a_calculation_search_mode(self):
        msg = Message.from_str(_SEARCH_MODE_PACKET)
        assert msg.current_A == pytest.approx(0.0)
        assert msg.raw_current_A == "0000"
        
    def test_battery_flag_extraction_low(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        assert msg.battery == "01"
        
    def test_battery_flag_extraction_ok(self):
        msg = Message.from_str(_SEARCH_MODE_PACKET)
        assert msg.battery == "00"

    @pytest.mark.parametrize(["input_string", "expected_crc"], [
        (_TRANSMITTER_PACKET, "0e24"),
        (_SEARCH_MODE_PACKET, "6fd8")
    ])
    def test_crc_extraction_transmitter(self, input_string, expected_crc):
        msg = Message.from_str(input_string)
        assert msg.crc == expected_crc
        
    def test_invalid_syncword_handling(self):
        msg = Message.from_str(_CORRUPTED_SYNCWORD_PACKET)
        assert msg is None
        
    def test_missing_syncword_handling(self):
        msg = Message.from_str(_MISSING_PREAMBLE_PACKET)
        assert msg is not None
        
    def test_too_short_message_handling(self):
        with pytest.raises((ValueError, IndexError)):
            Message.from_str(_TRANSMITTER_PACKET[:-10])
            
    def test_empty_string_handling(self):
        msg = Message.from_str("")
        assert msg is None


class TestMessageCRC:
    @pytest.mark.parametrize("input_string", [
        _TRANSMITTER_PACKET,
        _SEARCH_MODE_PACKET
    ])
    def test_valid_crc_transmitter_packet(self, input_string):
        msg = Message.from_str(input_string)
        assert msg.crc_result in [True, 1, -1]
        
    def test_invalid_crc_corrupted_crc_field(self):
        msg = Message.from_str(_CORRUPTED_CRC_PACKET)
        assert msg.crc_result is False
        
    def test_invalid_crc_corrupted_data(self):
        msg = Message.from_str(_CORRUPTED_DATA_PACKET)
        assert msg.crc_result is False
        
    def test_crc_left_shift_detection(self):
        msg = Message.from_str(_CRC_LEFT_SHIFT_PACKET)
        assert msg.crc_result == -1
            
    def test_crc_right_shift_detection(self):
        msg = Message.from_str(_CRC_RIGHT_SHIFT_PACKET)
        assert msg.crc_result == 1
            
    def test_calc_crc_returns_integer(self):
        hex_string = "0000800d000027b10000008e0100"
        crc = Message.calc_crc(hex_string)
        assert isinstance(crc, int)


class TestMessageToString:
    
    def test_transmitter_packet_output_format(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        output = msg.to_string()
        assert "DS:c58c" in output
        assert "PM:0000" in output
        assert "total:0027b1" in output
        assert "current:008e" in output
        assert "BAT_LOW: 01" in output
        assert "crc:0e24" in output
        
    def test_search_mode_packet_output_format(self):
        msg = Message.from_str(_SEARCH_MODE_PACKET)
        output = msg.to_string()
        assert "DS:c58c" in output
        assert "PM:ffff" in output
        assert "total:000000" in output
        assert "current:0000" in output
        assert "BAT_LOW: 00" in output
        assert "crc:6fd8" in output
        
    def test_power_calculation_in_output(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        output = msg.to_string()
        total_kWh = msg.total_Ah * VOLTS / 1000
        current_kW = msg.current_A * VOLTS / 1000
        assert f"{total_kWh:.3f}" in output
        assert f"{current_kW:.3f}" in output


class TestMessageEdgeCases:
    
    def test_maximum_total_ah_value(self):
        msg = Message.from_str(_MAX_TOTAL_AH_PACKET)
        if msg:
            expected_value = 0xFFFFFF * POWER_FACTOR
            assert msg.total_Ah == pytest.approx(expected_value)
            assert msg.raw_total_Ah == "ffffff"
        
    def test_maximum_current_a_value(self):
        msg = Message.from_str(_MAX_CURRENT_A_PACKET)
        if msg:
            expected_value = 0xFFFF * POWER_FACTOR
            assert msg.current_A == pytest.approx(expected_value)
            assert msg.raw_current_A == "ffff"
        
    def test_zero_values(self):
        msg = Message.from_str(_ZERO_VALUES_PACKET)
        assert msg.total_Ah == pytest.approx(0.0)
        assert msg.current_A == pytest.approx(0.0)
        
    def test_lowercase_hex_handling(self):
        msg = Message.from_str(_TRANSMITTER_PACKET.lower())
        assert msg is not None
        assert msg.raw_total_Ah == "0027b1"
        
    def test_uppercase_hex_handling(self):
        msg = Message.from_str(_TRANSMITTER_PACKET.upper())
        assert msg is not None
        assert msg.raw_total_Ah.lower() == "0027b1"


class TestPowerCalculations:
    
    def test_transmitter_total_ah_to_kwh(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        total_kWh = msg.total_Ah * VOLTS / 1000
        assert total_kWh == pytest.approx(24.28479, rel=1e-4)
        
    def test_transmitter_current_a_to_kw(self):
        msg = Message.from_str(_TRANSMITTER_PACKET)
        current_kW = msg.current_A * VOLTS / 1000
        assert current_kW == pytest.approx(0.33938, rel=1e-4)
        
    def test_search_mode_total_ah_to_kwh(self):
        msg = Message.from_str(_SEARCH_MODE_PACKET)
        total_kWh = msg.total_Ah * VOLTS / 1000
        assert total_kWh == pytest.approx(0.0)
        
    def test_search_mode_current_a_to_kw(self):
        msg = Message.from_str(_SEARCH_MODE_PACKET)
        current_kW = msg.current_A * VOLTS / 1000
        assert current_kW == pytest.approx(0.0)
