import unittest
from datetime import datetime
from unittest.mock import patch, Mock, PropertyMock
import mock.GPIO as GPIO
from mock.SDL_DS3231 import SDL_DS3231
from mock.adafruit_veml7700 import VEML7700
from src.intelligentoffice import IntelligentOffice, IntelligentOfficeError


class TestIntelligentOffice(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy_in_range_11_15_not_14_occupied(self, mock_input: Mock):
        office = IntelligentOffice()
        mock_input.return_value = True
        occupied = office.check_quadrant_occupancy(IntelligentOffice.INFRARED_PIN1)
        mock_input.assert_called_once_with(IntelligentOffice.INFRARED_PIN1)
        self.assertTrue(occupied)

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy_in_range_11_15_not_14_free(self, mock_input: Mock):
        office = IntelligentOffice()
        mock_input.return_value = False
        occupied = office.check_quadrant_occupancy(IntelligentOffice.INFRARED_PIN3)
        mock_input.assert_called_once_with(IntelligentOffice.INFRARED_PIN3)
        self.assertFalse(occupied)

    def test_check_quadrant_occupancy_out_range_11_15_inside(self):
        office = IntelligentOffice()
        self.assertRaises(IntelligentOfficeError, office.check_quadrant_occupancy, 14)

    def test_check_quadrant_occupancy_out_range_11_15_outside(self):
        office = IntelligentOffice()
        self.assertRaises(IntelligentOfficeError, office.check_quadrant_occupancy, 16)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, 'read_datetime')
    def test_manage_blinds_based_on_time_in_range(self, mock_datetime: Mock, mock_servo_angle: Mock):
        office = IntelligentOffice()
        office.blinds_open = False
        mock_datetime.return_value = datetime(day=18, month=12, year=2025, hour=8, minute=0)
        office.manage_blinds_based_on_time()
        mock_servo_angle.assert_called_once_with(12)
        self.assertTrue(office.blinds_open)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, 'read_datetime')
    def test_manage_blinds_based_on_time_in_range_but_saturday(self, mock_datetime: Mock, mock_servo_angle: Mock):
        office = IntelligentOffice()
        office.blinds_open = True
        mock_datetime.return_value = datetime(day=14, month=12, year=2025, hour=8, minute=0)
        office.manage_blinds_based_on_time()
        mock_servo_angle.assert_called_once_with(2)
        self.assertFalse(office.blinds_open)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, 'read_datetime')
    def test_manage_blinds_based_on_time_out_range(self, mock_datetime: Mock, mock_servo_angle: Mock):
        office = IntelligentOffice()
        office.blinds_open = True
        mock_datetime.return_value = datetime(day=18, month=12, year=2025, hour=20, minute=0)
        office.manage_blinds_based_on_time()
        mock_servo_angle.assert_called_once_with(2)
        self.assertFalse(office.blinds_open)

    @patch.object(GPIO, 'input')
    @patch.object(VEML7700, 'lux', new_callable=PropertyMock)
    @patch.object(GPIO, 'output')
    def test_manage_light_level_lower_than_500(self, mock_output: Mock, lux: Mock, mock_input: Mock):
        office = IntelligentOffice()
        mock_input.side_effect = [True, False, False, False]
        lux.return_value = 499
        office.light_on = False
        office.manage_light_level()
        mock_output.assert_called_once_with(IntelligentOffice.LED_PIN, GPIO.HIGH)
        self.assertTrue(office.light_on)

    @patch.object(GPIO, 'input')
    @patch.object(VEML7700, 'lux', new_callable=PropertyMock)
    @patch.object(GPIO, 'output')
    def test_manage_light_level_higher_than_550(self, mock_output: Mock, lux: Mock, mock_input: Mock):
        office = IntelligentOffice()
        mock_input.side_effect = [True, False, False, False]
        lux.return_value = 551
        office.light_on = True
        office.manage_light_level()
        mock_output.assert_called_once_with(IntelligentOffice.LED_PIN, GPIO.LOW)
        self.assertFalse(office.light_on)

    @patch.object(GPIO, 'input')
    @patch.object(VEML7700, 'lux', new_callable=PropertyMock)
    def test_manage_light_level_in_range_500_to_550(self, lux: Mock, mock_input: Mock):
        office = IntelligentOffice()
        mock_input.side_effect = [True, False, False, False]
        lux.return_value = 525
        office.light_on = True
        office.manage_light_level()
        self.assertTrue(office.light_on)

    @patch.object(VEML7700, 'lux', new_callable=PropertyMock)
    @patch.object(GPIO, 'output')
    @patch.object(GPIO, 'input')
    def test_manage_light_level_499_not_occupied(self, mock_input: Mock, mock_output: Mock, lux: Mock):
        office = IntelligentOffice()
        mock_input.side_effect = [False, False, False, False]
        lux.return_value = 499
        office.light_on = True
        office.manage_light_level()
        mock_output.assert_called_once_with(IntelligentOffice.LED_PIN, GPIO.LOW)
        self.assertFalse(office.light_on)

    @patch.object(GPIO, 'output')
    @patch.object(GPIO, 'input')
    def test_monitor_air_quality_detected(self, mock_input: Mock, mock_output: Mock):
        office = IntelligentOffice()
        mock_input.return_value = False
        office.monitor_air_quality()
        mock_input.assert_called_once_with(IntelligentOffice.GAS_PIN)
        mock_output.assert_called_once_with(IntelligentOffice.BUZZER_PIN, GPIO.HIGH)
        self.assertTrue(office.buzzer_on)
