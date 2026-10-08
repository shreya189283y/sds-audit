
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cas import is_valid_cas, find_cas


def test_water_is_valid():
    assert is_valid_cas("7732-18-5")


def test_nmp_is_valid():
    assert is_valid_cas("872-50-4")


def test_wrong_check_digit_is_invalid():
    assert not is_valid_cas("7732-18-4")


def test_find_cas_in_a_line():
    valid, invalid = find_cas("Water 7732-18-5 60-100%")
    assert valid == ["7732-18-5"]
    assert invalid == []


def test_bad_number_goes_to_invalid():
    valid, invalid = find_cas("Mystery chemical 7732-18-4")
    assert valid == []
    assert invalid == ["7732-18-4"]


def test_no_cas_numbers():
    valid, invalid = find_cas("Keep out of reach of children.")
    assert valid == []
    assert invalid == []