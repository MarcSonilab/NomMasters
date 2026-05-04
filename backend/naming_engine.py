def _vxx(n):
    return f"V{int(n):02d}"

def _video_name(ref, titol, fmt_seg, prf, lang, ver, vis, length, vxx, incl_ext):
    parts = [ref, "N", titol, "N", fmt_seg, prf, lang, ver, vis, length, "XXX", vxx]
    name = "-".join(parts)
    return name + ".mov" if incl_ext else name

def _audio_name(ref, titol, fmt_seg, prf, lang, ver, length, ta, cn, vxx, incl_ext):
    ta_cn = f"{ta}_{cn}"
    parts = [ref, "N", titol, "N", fmt_seg, prf, lang, ver, "XXX", length, ta_cn, vxx]
    name = "-".join(parts)
    return name + ".wav" if incl_ext else name

def _generate_for_episode(ref, titol, fmt_seg, params):
    prfs = params["prfs"]
    langs = params["langs"]
    visuals = params["visuals"]
    length = params["length"]
    ta_blocks = params.get("ta_blocks", [])
    gen_video = params.get("gen_video", True)
    gen_audio = params.get("gen_audio", False)
    incl_ext = params.get("incl_ext", False)
    vxx = _vxx(params.get("vxx", 1))

    videos = []
    audios = []

    if gen_video:
        for prf in prfs:
            for lang_obj in langs:
                lang = lang_obj["code"]
                ver = "ORG" if lang_obj["pin"] else "ALT"
                for vis in visuals:
                    videos.append(_video_name(ref, titol, fmt_seg, prf, lang, ver, vis, length, vxx, incl_ext))

    if gen_audio:
        for prf in prfs:
            for lang_obj in langs:
                lang = lang_obj["code"]
                ver = "ORG" if lang_obj["pin"] else "ALT"
                for block in ta_blocks:
                    ta = block["ta"]
                    for cn in block["channels"]:
                        audios.append(_audio_name(ref, titol, fmt_seg, prf, lang, ver, length, ta, cn, vxx, incl_ext))

    return {"video": videos, "audio": audios}

def generate_names(params):
    ref = params["ref"]
    titol = params["titol"]
    fmt = params["fmt"]
    tmp = params.get("tmp", 1)
    epi_from = params.get("epi_from", 1)
    epi_to = params.get("epi_to", 1)

    if fmt == "SER":
        episodes = []
        for epi in range(int(epi_from), int(epi_to) + 1):
            fmt_seg = f"SER_S{int(tmp):02d}_E{int(epi):04d}"
            ep_code = f"S{int(tmp):02d}E{int(epi):04d}"
            result = _generate_for_episode(ref, titol, fmt_seg, params)
            episodes.append({"code": ep_code, "video": result["video"], "audio": result["audio"]})
        return {"episodes": episodes}

    return _generate_for_episode(ref, titol, fmt, params)
