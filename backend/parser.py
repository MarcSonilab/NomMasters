import re

KNOWN_FMT = {"FTR", "TLR", "SPT"}
KNOWN_PRF = {"MASTER", "BR", "DCP", "SD"}
KNOWN_IDI = {"ES", "EN", "CA", "EU", "FR", "RU", "ZH", "JA", "NO", "CS", "XX"}
KNOWN_VER = {"ORG", "ALT"}
KNOWN_VIS = {"XXX", "GRA", "INT", "SBT", "GRA_INT", "GRA_SBT"}
KNOWN_LEN = {"S", "L"}
KNOWN_TA  = {"MIX", "ME", "DX", "XXX"}

def parse_name(raw: str) -> dict:
    result = {
        "ref": "", "titol": "", "fmt": "", "tmp": "", "epi": "",
        "prf": "", "idi": "", "ver": "", "vis": "", "length": "",
        "ta": "", "cn": "", "vxx": "", "ext": "", "file_type": "",
        "unknown": [],
    }

    # Split extension (only if last token after last dot is short)
    last_seg = raw.split("-")[-1]
    if "." in last_seg:
        dot = raw.rfind(".")
        result["ext"] = raw[dot:]
        raw = raw[:dot]

    # Split on -N-
    n_parts = raw.split("-N-")
    if len(n_parts) >= 2:
        result["ref"] = n_parts[0]
        rest = "-N-".join(n_parts[1:])
        n2 = rest.split("-N-", 1)
        result["titol"] = n2[0]
        remainder = n2[1] if len(n2) > 1 else ""
    else:
        remainder = raw

    segs = [s for s in remainder.split("-") if s]
    order = ["fmt", "prf", "idi", "ver", "vis", "length", "ta_cn", "vxx"]
    state = 0
    i = 0

    while i < len(segs) and state < len(order):
        seg = segs[i]
        field = order[state]

        if field == "fmt":
            if seg in KNOWN_FMT:
                result["fmt"] = seg
                i += 1; state += 1
            elif seg.startswith("SER"):
                m = re.match(r"SER_(S\d+)_(E\d+)", seg)
                if m:
                    result["fmt"] = "SER"
                    result["tmp"] = m.group(1)
                    result["epi"] = m.group(2)
                else:
                    result["fmt"] = "SER"
                i += 1; state += 1
            else:
                result["unknown"].append(seg); i += 1

        elif field == "prf":
            if seg in KNOWN_PRF:
                result["prf"] = seg; i += 1; state += 1
            else:
                result["unknown"].append(seg); i += 1

        elif field == "idi":
            if seg in KNOWN_IDI:
                result["idi"] = seg; i += 1; state += 1
            else:
                result["unknown"].append(seg); i += 1

        elif field == "ver":
            if seg in KNOWN_VER:
                result["ver"] = seg; i += 1; state += 1
            else:
                result["unknown"].append(seg); i += 1

        elif field == "vis":
            if seg in KNOWN_VIS:
                result["vis"] = seg; i += 1; state += 1
            else:
                result["unknown"].append(seg); i += 1

        elif field == "length":
            if seg in KNOWN_LEN:
                result["length"] = seg; i += 1; state += 1
            else:
                result["unknown"].append(seg); i += 1

        elif field == "ta_cn":
            if seg == "XXX":
                result["ta"] = "XXX"; result["cn"] = ""
                i += 1; state += 1
            else:
                m = re.match(r"(MIX|ME|DX)_(.*)", seg)
                if m:
                    result["ta"] = m.group(1)
                    result["cn"] = m.group(2)
                    i += 1; state += 1
                else:
                    result["unknown"].append(seg); i += 1

        elif field == "vxx":
            if re.match(r"V\d{2}", seg):
                result["vxx"] = seg; i += 1; state += 1
            else:
                result["unknown"].append(seg); i += 1
        else:
            i += 1

    while i < len(segs):
        result["unknown"].append(segs[i]); i += 1

    if result["ta"] == "XXX" or result["ext"] == ".mov":
        result["file_type"] = "video"
    elif result["ta"] in {"MIX", "ME", "DX"} or result["ext"] == ".wav":
        result["file_type"] = "audio"

    return result
