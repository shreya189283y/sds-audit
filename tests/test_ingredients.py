#parse_ingredients(section3) -> list of Ingredient(name, cas, conc_min, conc_max, raw_line).
# Handle '1-5%', '1 - 5', '<1', '>= 30', '10 to 30', and 'Proprietary'. 
# Keep raw_line so every value can be traced to the PDF.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extract import parse_concentration, parse_ingredients, check_undisclosed

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

def test_undisclosed_keyword():
    flag, evidence = check_undisclosed(FAKE_SECTION_3)
    assert flag is True
    assert evidence == "trade secret"


def test_fully_disclosed():
    section = """
Water 7732-18-5 60-100%
N-Methyl-2-pyrrolidone 872-50-4 1-5%
"""
    flag, evidence = check_undisclosed(section)
    assert flag is False
    assert evidence == ""


def test_no_cas_numbers_at_all():
    flag, evidence = check_undisclosed("Non Reportable")
    assert flag is True
    assert evidence == "no valid CAS numbers"


def test_ingredient_without_cas():
    section = """
Water 7732-18-5 60-100%
Propellant 0-5
"""
    flag, evidence = check_undisclosed(section)
    assert flag is True
    assert evidence == "no CAS for: Propellant"

def test_en_dash_range():
    assert parse_concentration("3 – 4% YES") == (3.0, 4.0)


def test_en_dash_range_with_decimal():
    assert parse_concentration("0.5 – 1%") == (0.5, 1.0)


def test_percent_and_bound_inside_range():
    assert parse_concentration("1% - < 3%") == (1.0, 3.0)


def test_bounds_on_both_ends():
    assert parse_concentration(">=5.0 – <=10.0") == (5.0, 10.0)


def test_footer_date_is_not_an_ingredient():
    line = "HIL00470 Version #: 02 Revision date: 12-19-2018 Issue date: 01-22-2015 1 / 6"
    assert parse_ingredients(line) == []