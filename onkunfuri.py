"""JMDictFurigana.ipynb
original file is located at https://colab.research.google.com/drive/1GFhalCG5pSvtsOEl0Y22NOg1UBGZPzau
"""

!pip -q install lxml pandas jaconv

import gzip, re
from lxml import etree
import pandas as pd
import jaconv

def load_kanjidic2(path_gz: str):
    d = {}
    with gzip.open(path_gz, "rb") as f:
        tree = etree.parse(f)

    for ch in tree.xpath("//character"):
        literal = ch.findtext("literal")
        if not literal:
            continue

        on = set()
        kun = set()
        for r in ch.xpath(".//reading_meaning/rmgroup/reading"):
            rtype = r.get("r_type")
            txt = (r.text or "").strip()
            if not txt:
                continue
            if rtype == "ja_on":
                on.add(jaconv.kata2hira(txt))   # normalize to hiragana for matching
            elif rtype == "ja_kun":
                kun.add(txt)                    # may contain dot and/or leading '-'

        d[literal] = {"on": on, "kun": kun}

    return d

kd = load_kanjidic2("kanjidic2.xml.gz")
print("KANJIDIC2 loaded:", len(kd))

KANJI_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF々〆ヵヶ]")
KANA_CHAR_RE = re.compile(r"[ぁ-ゖァ-ヺー]")  # hira/kata/ー

def is_kana_char(ch: str) -> bool:
    return bool(KANA_CHAR_RE.fullmatch(ch))

def parse_mapping(map_str: str):
    """
    "0:に;1:くず" -> [(0,0,"に"), (1,1,"くず")]
    "0-2:きょう" -> [(0,2,"きょう")]
    """
    segments = []
    map_str = (map_str or "").strip()
    if not map_str:
        return segments

    for part in map_str.split(";"):
        part = part.strip()
        if not part:
            continue
        idx, rd = part.split(":", 1)
        idx = idx.strip()
        rd = rd.strip()

        if "-" in idx:
            a, b = idx.split("-", 1)
            start, end = int(a), int(b)
        else:
            start = end = int(idx)

        segments.append((start, end, rd))
    return segments

def build_bracketed(headword: str, mapping_str: str):
    chars = list(headword)
    n = len(chars)

    segments = parse_mapping(mapping_str)
    start_map = {s: (e, r) for s, e, r in segments}

    tokens = []
    flags = []

    # If any range segment covers >1 char, flag it (jukujikun/ateji-like)
    if any(e > s for s, e, _ in segments):
        flags.append("当て字・熟字訓")

    i = 0
    while i < n:
        if i in start_map:
            end, rd = start_map[i]
            seg = "".join(chars[i:end+1])
            token = f"{seg}[{rd}]"
            i = end + 1

            # attach following kana (okurigana / kana tail) to this token
            while i < n and i not in start_map and is_kana_char(chars[i]):
                token += chars[i]
                i += 1

            tokens.append(token)
        else:
            ch = chars[i]
            # attach stray kana to previous token if possible
            if tokens and is_kana_char(ch):
                tokens[-1] += ch
            else:
                tokens.append(ch)
            i += 1

    # join tokens with spaces, but don't split pure-kana continuations unnecessarily
    # (most of the time tokens are already merged appropriately)
    furigana = " ".join(tokens)
    return furigana, " ".join(sorted(set(flags)))

# test some example entries to ensure conversion is working
for line in [
    "煮崩れ|にくずれ|0:に;1:くず",
    "赤十字条約|せきじゅうじじょうやく|0:せき;1:じゅう;2:じ;3:じょう;4:やく",
    "赤ゲット|あかゲット|0:あか",
    "経帷子|きょうかたびら|0-2:きょうかたびら",
]:
    head, yomi, m = line.split("|")
    furi, flg = build_bracketed(head, m)
    print(head, "=>", furi, "| flags:", flg)

BRACKET_RE = re.compile(
    r"(?P<seg>[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF々〆ヵヶ]+)"
    r"(?:\x5B|［)(?P<r>[^]\］]+)(?:\x5D|］)"
)

def normalize_kun_string(k: str) -> str:
    return k.strip().lstrip("-")

def kun_variants(kun: str):
    k = normalize_kun_string(kun)
    if "." in k:
        head = k.split(".", 1)[0]
        joined = k.replace(".", "")
        return {head, joined}
    return {k}

# deal with sokuon variants
def on_variants(on_hira: str):
    vs = {on_hira}
    if on_hira and on_hira[-1] in ("く", "き", "つ", "ち"):
        vs.add(on_hira[:-1] + "っ")
    return vs

def classify_on_kun_single_kanji(kanji: str, reading_hira: str, kd):
    info = kd.get(kanji)
    if not info:
        return "unknown"

    f = reading_hira.strip()

    on_set = set()
    for o in info["on"]:
        on_set |= on_variants(o.strip())

    kun_set = set()
    for k in info["kun"]:
        for v in kun_variants(k):
            kun_set.add(v.strip())

    is_on = f in on_set
    is_kun = f in kun_set

    if is_on and is_kun:
        return "ambiguous"
    if is_on:
        return "on"
    if is_kun:
        return "kun"
    return "unknown"

def convert_onkun_in_text(text: str, kd):
    flags = []

    def repl(m):
        seg = m.group("seg")   # may be 1+ kanji
        r = m.group("r")

        # Only attempt 音/訓 classification when seg is exactly 1 kanji
        if len(seg) == 1 and KANJI_RE.fullmatch(seg):
            # Only process if reading is hiragana-ish; otherwise leave
            # (JMdictFurigana readings are usually hiragana)
            kind = classify_on_kun_single_kanji(seg, r, kd)
            if kind == "on":
                return f"{seg}[{jaconv.hira2kata(r)}]"
            else:
                if kind in ("unknown", "ambiguous"):
                    flags.append(kind)
                return f"{seg}[{r}]"
        else:
            # multi-kanji bracket: leave as-is
            flags.append("multi_kanji_furi")
            return m.group(0)

    out = BRACKET_RE.sub(repl, text)
    return out, " ".join(sorted(set(flags)))

# test to ensure hiragana to katakana is working
print(convert_onkun_in_text("水[すい] 曜[よう] 日[び]", kd))

def process_jmdictfurigana(txt_path: str, kd, limit=None):
    rows = []
    with open(txt_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split("|")
            if len(parts) != 3:
                continue

            headword, yomi, mapping = parts

            furi1, flags1 = build_bracketed(headword, mapping)
            furi2, flags2 = convert_onkun_in_text(furi1, kd)

            flags = " ".join(sorted(set((flags1 + " " + flags2).split()))).strip()

            rows.append({
                "語彙": headword,
                "読み方": yomi,
                "振り仮名": furi2,
                "変換フラグ": flags
            })
    return pd.DataFrame(rows)

df = process_jmdictfurigana("JmdictFurigana.txt", kd)
print("rows:", len(df))
df.head(10)

# create export csv file
OUT = "JmdictFurigana_onkun.csv"
df.to_csv(OUT, index=False)
OUT
