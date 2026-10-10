
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extract import split_sections


def test_section_3_colon_caps():
    text = """
SECTION 3: COMPOSITION
Water 7732-18-5 60-100%
SECTION 4: FIRST AID MEASURES
Rinse with water.
"""
    sections = split_sections(text)
    assert 3 in sections
    assert "7732-18-5" in sections[3]
    assert "Rinse" not in sections[3]


def test_number_dot_title():
    text = """
3. Composition/Information on Ingredients
Water 7732-18-5 60-100%
4. First Aid Measures
Rinse with water.
"""
    sections = split_sections(text)
    assert 3 in sections
    assert "Rinse" not in sections[3]


def test_section_3_hyphen():
    text = """
Section 3 - Composition
Water 7732-18-5 60-100%
Section 4 - First aid
Rinse with water.
"""
    sections = split_sections(text)
    assert 3 in sections
    assert "Rinse" not in sections[3]


def test_old_format_composition_is_section_2():
    text = """
SECTION 2: COMPOSITION/INFORMATION ON INGREDIENTS
Water 7732-18-5 60-100%
SECTION 3: PHYSICAL CHARACTERISTICS
Boiling point 212
"""
    sections = split_sections(text)
    assert 3 in sections
    assert "7732-18-5" in sections[3]
    assert "Boiling" not in sections[3]


def test_spelled_out_number():
    text = """
Section Two Composition/Information on Ingredients
Water 7732-18-5 60-100%
Section Three Hazards Identification
May cause irritation.
"""
    sections = split_sections(text)
    assert 3 in sections
    assert "irritation" not in sections[3]


def test_short_ingredients_title():
    text = """
2. INGREDIENTS
Water 7732-18-5 60-100%
3. PHYSICAL DATA
Boiling point 212
"""
    sections = split_sections(text)
    assert 3 in sections
    assert "Boiling" not in sections[3]


def test_hazardous_ingredients_is_composition():
    text = """
SECTION 2: HAZARDOUS INGREDIENTS
Water 7732-18-5 60-100%
SECTION 3: PHYSICAL DATA
Boiling point 212
"""
    sections = split_sections(text)
    assert 3 in sections
    assert 2 not in sections