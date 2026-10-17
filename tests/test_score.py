import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.score import score

NMP = "872-50-4"
WATER = "7732-18-5"
OXYBENZONE = "131-57-7"
QUARTZ = "14808-60-7"
LIMONENE = "5989-27-5"


def test_high():
    assert score([NMP, WATER], False)["level"] == "HIGH"


def test_medium_ed_list_ii_iii():
    assert score([OXYBENZONE, WATER], False)["level"] == "MEDIUM"


def test_medium_conditional():
    assert score([QUARTZ, WATER], False)["level"] == "MEDIUM"


def test_hit_outranks_undisclosed():
    result = score([OXYBENZONE, WATER], True)
    assert result["level"] == "MEDIUM"
    assert result["undisclosed"] is True


def test_undisclosed():
    assert score([WATER, LIMONENE], True)["level"] == "UNDISCLOSED"


def test_low():
    assert score([WATER, LIMONENE], False)["level"] == "LOW"


def test_empty_product():
    assert score([], False)["level"] == "LOW"


def test_flags_remember_cas():
    flags = score([NMP, WATER], False)["flags"]
    assert all(flag["cas"] == NMP for flag in flags)