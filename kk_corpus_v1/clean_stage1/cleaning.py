import html
import re
import unicodedata

_HTML_ENTITIES = {
    "&amp;": "&",
    "&laquo;": "«",
    "&raquo;": "»",
    "&quot;": '"',
    "&nbsp;": " ",
}

_C_ESCAPE_REPLACEMENTS = [
    ("\\n", "\n"),
    ("\\t", "\t"),
    ("\\r", "\r"),
]


def fix_escape_sequences(text: str) -> str:
    if not isinstance(text, str):
        return text

    for escaped, real in _C_ESCAPE_REPLACEMENTS:
        text = text.replace(escaped, real)

    for bad, good in _HTML_ENTITIES.items():
        text = text.replace(bad, good)
    text = html.unescape(text)
    return text


def remove_corrupted_paragraphs(text: str, min_paragraphs: int = 1) -> str | None:

    if not isinstance(text, str):
        return None

    paragraphs = text.split("\n")
    cleaned = [p for p in paragraphs if "\ufffd" not in p]  # \ufffd == �

    cleaned = [p for p in cleaned if p.strip()]

    if len(cleaned) < min_paragraphs:
        return None

    return "\n".join(cleaned)

_CYR_TO_LAT = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y",
    "х": "x", "к": "k", "м": "m", "т": "t", "в": "b", "н": "h",
    "і": "i",
    "А": "A", "Е": "E", "О": "O", "Р": "P", "С": "C", "У": "Y",
    "Х": "X", "К": "K", "М": "M", "Т": "T", "В": "B", "Н": "H",
    "І": "I",
}
_LAT_TO_CYR = {v: k for k, v in _CYR_TO_LAT.items()}



_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def fix_homoglyphs(text: str, allowlist: set[str] | None = None) -> str:
    allowlist = {w.lower() for w in (allowlist or set())}

    def repl(match: re.Match) -> str:
        word = match.group(0)

        if word.lower() in allowlist:
            return word


        unambig_cyr = sum(1 for ch in word if "\u0400" <= ch <= "\u04FF")
        unambig_lat = sum(1 for ch in word if ch.isascii() and ch.isalpha())

        if unambig_cyr == 0 and unambig_lat == 0:
            return word

        target_cyr = unambig_cyr >= unambig_lat

        out = []
        for ch in word:
            if target_cyr and ch in _LAT_TO_CYR:
                out.append(_LAT_TO_CYR[ch])
            elif not target_cyr and ch in _CYR_TO_LAT:
                out.append(_CYR_TO_LAT[ch])
            else:
                out.append(ch)
        return "".join(out)

    return _WORD_RE.sub(repl, text)

_REPEAT_PUNCT_RE = re.compile(r"([!?.,;:\-])\1{2,}")


def collapse_repeated_punctuation(text: str, max_repeat: int = 3) -> str:
     return _REPEAT_PUNCT_RE.sub(lambda m: m.group(1) * max_repeat, text)


_HTML_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")
_INVISIBLE_CHARS_RE = re.compile(
    "[" + "".join([
        "\u200b", "\u200c", "\u200d",
        "\u200e", "\u200f",
        "\ufeff",
        "\u00ad",
    ]) + "]"
)


def remove_html_boilerplate(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = _HTML_TAG_RE.sub(" ", text)
    text = _INVISIBLE_CHARS_RE.sub("", text)
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

_SPAM_KEYWORDS = [
    # casino
    "казино", "casino", "слот", "бонус код", "фриспин", "джекпот",
    "ставки на спорт", "1xbet", "мостбет", "букмекер",
    "казино вулкан", "pox casino", "softswiss",
    # adult
    "porn", "porno", "порно", "порнуха", "xxx", "эскорт", "интим услуги", "18+",
    "kazakwa", "секс", "проститутки", "девственниц", "страпон",
    "ебля", "блять", "creampies", "свингеров", "тосек лаззаты",
]

_EMOJI_RE = re.compile(
    "[" + "".join([
        "\U0001F300-\U0001FAFF",
        "\U00002700-\U000027BF",
        "\U0001F1E6-\U0001F1FF",
    ]) + "]"
)


def is_spam(text: str, keyword_threshold: int = 2, emoji_ratio_threshold: float = 0.02) -> bool:

    if not isinstance(text, str) or not text.strip():
        return False

    lowered = text.lower()

    kw_hits = sum(1 for kw in _SPAM_KEYWORDS if kw in lowered)

    emoji_count = len(_EMOJI_RE.findall(text))
    emoji_ratio = emoji_count / max(len(text), 1)

    if kw_hits >= keyword_threshold:
        return True
    if emoji_ratio >= emoji_ratio_threshold and kw_hits >= 1:
        return True

    return False


def clean_document(text: str, homoglyph_allowlist = None, on_step=None) -> str:
    if not isinstance(text, str) or not text.strip():
        return None

    text = fix_escape_sequences(text)
    if on_step:
        on_step("fix_escape_sequences", text)

    text = remove_corrupted_paragraphs(text, min_paragraphs=1)
    if on_step:
        on_step("remove_corrupted_paragraphs", text)
    if text is None:
        return None

    text = fix_homoglyphs(text, allowlist=homoglyph_allowlist)
    if on_step:
        on_step("fix_homoglyphs", text)

    text = collapse_repeated_punctuation(text)
    if on_step:
        on_step("collapse_repeated_punctuation", text)

    text = remove_html_boilerplate(text)
    if on_step:
        on_step("remove_html_boilerplate", text)

    if not text.strip():
        return None

    if is_spam(text):
        if on_step:
            on_step("is_spam", None)
        return None
    return text