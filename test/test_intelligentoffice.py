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
        mock_servo_angle.assert_called_once_with(2)
        self.assertTrue(office.blinds_open)

