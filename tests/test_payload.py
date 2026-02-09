import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from payload import Message, SYNCWORD, POWER_FACTOR, VOLTS
import pytest


class TestMessageFromStr:
    
    def test_from_str_transmitter_packet(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg is not None
        assert msg.raw == transmitter_packet
        
    def test_from_str_search_mode_packet(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        assert msg is not None
        assert msg.raw == search_mode_packet
        
    def test_field_extraction_receiver_id(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.receiver_id == "c58c"
        
    def test_field_extraction_sender_id_transmitter(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.sender_id == "0000"
        
    def test_field_extraction_sender_id_search_mode(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        assert msg.sender_id == "ffff"
        
    def test_field_extraction_u1_transmitter(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.u1 == "80"
        
    def test_field_extraction_u1_search_mode(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        assert msg.u1 == "10"
        
    def test_field_extraction_u2(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.u2 == "0d"
        
    def test_field_extraction_u3(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.u3 == "00"
        
    def test_total_ah_calculation_transmitter(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.total_Ah == pytest.approx(101.61)
        
    def test_total_ah_raw_value_transmitter(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.raw_total_Ah == "0027b1"
        
    def test_total_ah_calculation_search_mode(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        assert msg.total_Ah == pytest.approx(0.0)
        
    def test_total_ah_raw_value_search_mode(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        assert msg.raw_total_Ah == "000000"
        
    def test_current_a_calculation_transmitter(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.current_A == pytest.approx(1.42)
        
    def test_current_a_raw_value_transmitter(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.raw_current_A == "008e"
        
    def test_current_a_calculation_search_mode(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        assert msg.current_A == pytest.approx(0.0)
        
    def test_current_a_raw_value_search_mode(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        assert msg.raw_current_A == "0000"
        
    def test_battery_flag_extraction_low(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.battery == "01"
        
    def test_battery_flag_extraction_ok(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        assert msg.battery == "00"
        
    def test_crc_extraction_transmitter(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.crc == "0e24"
        
    def test_crc_extraction_search_mode(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        assert msg.crc == "6fd8"
        
    def test_raw_string_preservation(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.raw == transmitter_packet
        
    def test_invalid_syncword_handling(self, corrupted_syncword_packet):
        msg = Message.from_str(corrupted_syncword_packet)
        assert msg is None
        
    def test_missing_syncword_handling(self, missing_preamble_packet):
        msg = Message.from_str(missing_preamble_packet)
        assert msg is not None
        
    def test_too_short_message_handling(self, too_short_packet):
        with pytest.raises((ValueError, IndexError)):
            Message.from_str(too_short_packet)
            
    def test_empty_string_handling(self, empty_packet):
        msg = Message.from_str(empty_packet)
        assert msg is None


class TestMessageCRC:
    
    def test_valid_crc_transmitter_packet(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        assert msg.crc_result is True
        
    def test_valid_crc_search_mode_packet(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        assert msg.crc_result == -1
        
    def test_invalid_crc_corrupted_crc_field(self, corrupted_crc_packet):
        msg = Message.from_str(corrupted_crc_packet)
        assert msg.crc_result is False
        
    def test_invalid_crc_corrupted_data(self, corrupted_data_packet):
        msg = Message.from_str(corrupted_data_packet)
        assert msg.crc_result is False
        
    def test_crc_left_shift_detection(self, crc_left_shift_packet):
        msg = Message.from_str(crc_left_shift_packet)
        assert msg.crc_result == -1
            
    def test_crc_right_shift_detection(self, crc_right_shift_packet):
        msg = Message.from_str(crc_right_shift_packet)
        assert msg.crc_result == 1
            
    def test_calc_crc_returns_integer(self):
        hex_string = "0000800d000027b10000008e0100"
        crc = Message.calc_crc(hex_string)
        assert isinstance(crc, int)


class TestMessageToString:
    
    def test_transmitter_packet_output_format(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        output = msg.to_string()
        assert "DS:c58c" in output
        assert "PM:0000" in output
        assert "total:0027b1" in output
        assert "current:008e" in output
        assert "BAT_LOW: 01" in output
        assert "crc:0e24" in output
        
    def test_search_mode_packet_output_format(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        output = msg.to_string()
        assert "DS:c58c" in output
        assert "PM:ffff" in output
        assert "total:000000" in output
        assert "current:0000" in output
        assert "BAT_LOW: 00" in output
        assert "crc:6fd8" in output
        
    def test_power_calculation_in_output(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        output = msg.to_string()
        total_kWh = msg.total_Ah * VOLTS / 1000
        current_kW = msg.current_A * VOLTS / 1000
        assert f"{total_kWh:.3f}" in output
        assert f"{current_kW:.3f}" in output


class TestMessageEdgeCases:
    
    def test_maximum_total_ah_value(self, max_total_ah_packet):
        msg = Message.from_str(max_total_ah_packet)
        if msg:
            expected_value = 0xFFFFFF * POWER_FACTOR
            assert msg.total_Ah == pytest.approx(expected_value)
            assert msg.raw_total_Ah == "ffffff"
        
    def test_maximum_current_a_value(self, max_current_a_packet):
        msg = Message.from_str(max_current_a_packet)
        if msg:
            expected_value = 0xFFFF * POWER_FACTOR
            assert msg.current_A == pytest.approx(expected_value)
            assert msg.raw_current_A == "ffff"
        
    def test_zero_values(self, zero_values_packet):
        msg = Message.from_str(zero_values_packet)
        assert msg.total_Ah == pytest.approx(0.0)
        assert msg.current_A == pytest.approx(0.0)
        
    def test_lowercase_hex_handling(self, lowercase_packet):
        msg = Message.from_str(lowercase_packet)
        assert msg is not None
        assert msg.raw_total_Ah == "0027b1"
        
    def test_uppercase_hex_handling(self, uppercase_packet):
        msg = Message.from_str(uppercase_packet)
        assert msg is not None
        assert msg.raw_total_Ah.lower() == "0027b1"


class TestPowerCalculations:
    
    def test_transmitter_total_ah_to_kwh(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        total_kWh = msg.total_Ah * VOLTS / 1000
        assert total_kWh == pytest.approx(24.28479, rel=1e-4)
        
    def test_transmitter_current_a_to_kw(self, transmitter_packet):
        msg = Message.from_str(transmitter_packet)
        current_kW = msg.current_A * VOLTS / 1000
        assert current_kW == pytest.approx(0.33938, rel=1e-4)
        
    def test_search_mode_total_ah_to_kwh(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        total_kWh = msg.total_Ah * VOLTS / 1000
        assert total_kWh == pytest.approx(0.0)
        
    def test_search_mode_current_a_to_kw(self, search_mode_packet):
        msg = Message.from_str(search_mode_packet)
        current_kW = msg.current_A * VOLTS / 1000
        assert current_kW == pytest.approx(0.0)
