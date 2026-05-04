import pytest
from backend.naming_engine import generate_names

BASE = dict(
    ref="1983", titol="BABA_YAGA", fmt="FTR",
    tmp=1, epi_from=1, epi_to=1,
    prfs=["MASTER"],
    langs=[{"code": "ES", "pin": True}],
    visuals=["XXX"],
    length="S",
    ta_blocks=[],
    vxx=1,
    gen_video=True, gen_audio=False,
    incl_ext=False,
)

def test_simple_video_name():
    result = generate_names(BASE)
    assert result["video"] == ["1983-N-BABA_YAGA-N-FTR-MASTER-ES-ORG-XXX-S-XXX-V01"]

def test_alt_lang_gives_alt_ver():
    p = {**BASE, "langs": [{"code": "EN", "pin": False}]}
    result = generate_names(p)
    assert result["video"] == ["1983-N-BABA_YAGA-N-FTR-MASTER-EN-ALT-XXX-S-XXX-V01"]

def test_extension_added_when_toggle_on():
    p = {**BASE, "incl_ext": True}
    result = generate_names(p)
    assert result["video"][0].endswith(".mov")

def test_audio_name_has_ta_cn():
    p = {**BASE, "gen_video": False, "gen_audio": True,
         "ta_blocks": [{"ta": "MIX", "channels": ["2_0"]}]}
    result = generate_names(p)
    assert result["audio"] == ["1983-N-BABA_YAGA-N-FTR-MASTER-ES-ORG-XXX-S-MIX_2_0-V01"]

def test_audio_always_vis_xxx():
    p = {**BASE, "gen_video": False, "gen_audio": True,
         "visuals": ["GRA"],
         "ta_blocks": [{"ta": "MIX", "channels": ["2_0"]}]}
    result = generate_names(p)
    assert "-XXX-" in result["audio"][0]

def test_multiple_prfs_and_langs():
    p = {**BASE,
         "prfs": ["MASTER", "DCP"],
         "langs": [{"code": "ES", "pin": True}, {"code": "EN", "pin": False}]}
    result = generate_names(p)
    assert len(result["video"]) == 4  # 2 prfs x 2 langs x 1 vis

def test_ser_mode():
    p = {**BASE, "fmt": "SER", "tmp": 1, "epi_from": 1, "epi_to": 2}
    result = generate_names(p)
    assert "episodes" in result
    assert len(result["episodes"]) == 2
    ep1 = result["episodes"][0]
    assert ep1["code"] == "S01E0001"
    assert "SER_S01_E0001" in ep1["video"][0]

def test_vxx_version():
    p = {**BASE, "vxx": 3}
    result = generate_names(p)
    assert result["video"][0].endswith("-V03")

def test_multiple_ta_channels():
    p = {**BASE, "gen_video": False, "gen_audio": True,
         "ta_blocks": [{"ta": "MIX", "channels": ["2_0", "5_1"]}]}
    result = generate_names(p)
    assert len(result["audio"]) == 2

def test_multiple_visuals():
    p = {**BASE, "visuals": ["XXX", "GRA"]}
    result = generate_names(p)
    assert len(result["video"]) == 2
