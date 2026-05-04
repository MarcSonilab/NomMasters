import pytest
from backend.parser import parse_name

def test_full_video_name():
    raw = "1983-N-BABA_YAGA-N-FTR-MASTER-ES-ORG-XXX-S-XXX-V01.mov"
    r = parse_name(raw)
    assert r["ref"] == "1983"
    assert r["titol"] == "BABA_YAGA"
    assert r["fmt"] == "FTR"
    assert r["prf"] == "MASTER"
    assert r["idi"] == "ES"
    assert r["ver"] == "ORG"
    assert r["vis"] == "XXX"
    assert r["length"] == "S"
    assert r["ta"] == "XXX"
    assert r["vxx"] == "V01"
    assert r["ext"] == ".mov"
    assert r["file_type"] == "video"

def test_audio_name():
    raw = "1983-N-BABA_YAGA-N-FTR-MASTER-ES-ORG-XXX-S-MIX_2_0-V01.wav"
    r = parse_name(raw)
    assert r["ta"] == "MIX"
    assert r["cn"] == "2_0"
    assert r["ext"] == ".wav"
    assert r["file_type"] == "audio"

def test_ser_mode():
    raw = "1983-N-BABA_YAGA-N-SER_S01_E0001-MASTER-ES-ORG-XXX-S-XXX-V01"
    r = parse_name(raw)
    assert r["fmt"] == "SER"
    assert r["tmp"] == "S01"
    assert r["epi"] == "E0001"

def test_no_extension():
    raw = "1983-N-BABA_YAGA-N-FTR-MASTER-ES-ORG-XXX-S-XXX-V01"
    r = parse_name(raw)
    assert r["ext"] == ""

def test_unknown_segment_flagged():
    raw = "1983-N-BABA_YAGA-N-FTR-MASTER-ES-ORG-XXX-S-UNKNOWN-V01"
    r = parse_name(raw)
    assert len(r["unknown"]) > 0

def test_gra_vis():
    raw = "1983-N-BABA_YAGA-N-FTR-MASTER-ES-ORG-GRA-S-XXX-V01.mov"
    r = parse_name(raw)
    assert r["vis"] == "GRA"

def test_mix_51():
    raw = "1983-N-BABA_YAGA-N-FTR-MASTER-ES-ORG-XXX-S-MIX_5_1-V01.wav"
    r = parse_name(raw)
    assert r["ta"] == "MIX"
    assert r["cn"] == "5_1"

def test_long_version():
    raw = "1983-N-BABA_YAGA-N-FTR-MASTER-ES-ORG-XXX-L-XXX-V12"
    r = parse_name(raw)
    assert r["length"] == "L"
    assert r["vxx"] == "V12"
