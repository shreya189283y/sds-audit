#parse_ingredients(section3) -> list of Ingredient(name, cas, conc_min, conc_max, raw_line).
# Handle '1-5%', '1 - 5', '<1', '>= 30', '10 to 30', and 'Proprietary'. 
# Keep raw_line so every value can be traced to the PDF.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extract import parse_concentration, parse_ingredients

def test_simple_range():
    assert parse_concentration("1-5%") == (1.0,5.0)

def test_range_with_spaces():
    assert parse_concentration("1 - 5") ==(1.0, 5.0)

def test_range_with_to():
    assert parse_concentration("10 to 30")==(10.0, 30.0)

def test_less_than():
    assert parse_concentration("<1") == (0.0, 1.0)

def test_greater_or_equal():
    assert parse_concentration(">= 30")==(30.0, 100.0)

def test_single_value():
    assert parse_concentration("5%") == (5.0, 5.0)

def test_proprietary():
    assert parse_concentration("Proprietary")==(None, None)

def test_over_100_is_rejected():
    assert parse_concentration("231-791") ==(None, None)

FAKE_SECTION_3 = """
3. COMPOSITION / INFORMATION ON INGREDIENTS
Chemical name CAS No. Weight %
Water 7732-18-5 60-100%
N-Methyl-2-pyrrolidone 872-50-4 1-5%
Proprietary surfactant blend Trade secret 5-10%
"""

def test_normal_rows():
    result = parse_ingredients(FAKE_SECTION_3)
    assert len(result) == 3
    assert result[0].name == "Water"
    assert result[0].cas == "7732-18-5"
    assert result[1].cas == "872-50-4"
    assert result[1].conc_min == 1.0
    assert result[1].conc_max == 5.0


def test_proprietary_row():
    result = parse_ingredients(FAKE_SECTION_3)
    assert result[2].cas is None
    assert result[2].conc_min == 5.0
    assert result[2].conc_max == 10.0


def test_empty_input():
    assert parse_ingredients("") == []