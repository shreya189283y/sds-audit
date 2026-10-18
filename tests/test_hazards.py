import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hazards import lookup, is_safer


def list_names(hits):
    return [hit["list_name"] for hit in hits]


def test_nmp_on_prop65_and_svhc():
    names = list_names(lookup("872-50-4"))
    assert "Prop 65" in names
    assert "EU SVHC" in names


def test_glyphosate_on_prop65():
    assert "Prop 65" in list_names(lookup("1071-83-6"))


def test_water_has_no_hits():
    assert lookup("7732-18-5") == []


def test_is_safer():
    assert is_safer("7732-18-5") is True
    assert is_safer("872-50-4") is False


def test_npe_no_duplicate_hits():
    hits = lookup("9016-45-9")
    names = list_names(hits)
    assert "EU SVHC" in names
    assert "EU ED List I" in names
    rows = [(h["list_name"], h["endpoint"]) for h in hits]
    assert len(rows) == len(set(rows))


def test_lead_through_group():
    hits = lookup("7439-92-1")
    groups = [h["via_group"] for h in hits]
    assert "Lead and lead compounds" in groups
    assert "EU SVHC" in list_names(hits)


def test_silica_hit_carries_condition():
    hits = lookup("14808-60-7")
    assert len(hits) == 1
    assert "respirable" in hits[0]["condition"]


def test_glyphosate_salt_through_group():
    hits = lookup("38641-94-0")
    assert "Prop 65" in list_names(hits)
    assert hits[0]["via_group"] == "Glyphosate"


def test_ethylene_glycol_is_conditional():
    hits = lookup("107-21-1")
    assert hits[0]["list_name"] == "Prop 65"
    assert "ingested" in hits[0]["condition"]


def test_nmp_is_not_conditional():
    assert all(h["condition"] == "" for h in lookup("872-50-4"))