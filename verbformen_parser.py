from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from html import unescape
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


BASE_URL = "https://www.verbformen.com/?w={word}"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)


@dataclass
class VerbformenEntry:
    word: str
    article: str | None
    description: str | None
    principal_parts: list[str]
    auxiliary: str | None
    level: str | None
    translations: dict[str, list[str]]
    examples: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def format_verbformen_entry(entry: VerbformenEntry) -> str:
    word = f"{entry.article} {entry.word}" if entry.article else entry.word
    lines = [f"New daily word: {word}"]

    if entry.level:
        lines.append(f"Level: {entry.level}")

    if entry.principal_parts:
        lines.append(f"Principal parts: {', '.join(entry.principal_parts)}")

    if entry.auxiliary:
        lines.append(f"Auxiliary: {entry.auxiliary}")

    for lang in ("en", "ru"):
        translations = entry.translations.get(lang)
        if translations:
            lines.append(f"{lang.upper()}: {', '.join(translations[:8])}")

    if entry.examples:
        lines.append("Examples:")
        lines.extend(f"  - {example}" for example in entry.examples[:3])

    return "\n".join(lines)


def fetch_html(word: str, timeout: int = 15) -> tuple[str, str]:
    url = BASE_URL.format(word=quote_plus(word.strip()))
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace"), url


def parse_verbformen_html(html: str, word: str, url: str | None = None) -> VerbformenEntry:
    description = _first_meta_content("description", html)
    intro = _first_text(r"<h1[^>]*>.*?</h1>\s*<p[^>]*>(.*?)</p>", html)

    return VerbformenEntry(
        word=word,
        article=_parse_article(intro, html),
        description=description,
        principal_parts=_parse_principal_parts(intro),
        auxiliary=_parse_auxiliary(intro),
        level=_parse_level(intro),
        translations=_parse_translations(html),
        examples=_parse_examples(html),
    )


def parse_verbformen(word: str, timeout: int = 15) -> VerbformenEntry:
    html, url = fetch_html(word, timeout=timeout)
    return parse_verbformen_html(html, word=word, url=url)


def _parse_principal_parts(text: str | None) -> list[str]:
    if not text:
        return []

    match = re.search(r'principal parts of "[^"]+" are (.*?)\.', text, re.I)
    if not match:
        return []

    return re.findall(r'"([^"]+)"', match.group(1))


def _parse_auxiliary(text: str | None) -> str | None:
    if not text:
        return None

    match = re.search(r"auxiliary verb of .*? is ([a-zäöüß]+)", text, re.I)
    return match.group(1) if match else None


def _parse_level(text: str | None) -> str | None:
    if not text:
        return None

    match = re.search(r"vocabulary at ([A-C][12]) level", text)
    return match.group(1) if match else None


def _parse_article(text: str | None, html: str) -> str | None:
    if text:
        match = re.search(r'The article is "(der|die|das)\b', text, re.I)
        if match:
            return match.group(1).lower()

    match = re.search(r'<span[^>]*class="[^"]*\bvGrnd\b[^"]*"[^>]*>(.*?)</span>', html, re.S)
    if not match:
        return None

    text = _clean_html(match.group(1))
    match = re.match(r"(der|die|das)\b", text, re.I)
    return match.group(1).lower() if match else None


def _parse_translations(html: str) -> dict[str, list[str]]:
    translations: dict[str, list[str]] = {}
    for lang, body in re.findall(r'<dd\s+lang="([^"]+)"[^>]*>(.*?)</dd>', html, re.S):
        if lang not in {"en", "ru"}:
            continue

        spans = re.findall(r"<span[^>]*>(.*?)</span>", body, re.S)
        if not spans:
            continue

        text = _clean_html(spans[-1])
        if text:
            translations[lang] = [item.strip() for item in text.split(",") if item.strip()]

    return translations


def _parse_examples(html: str) -> list[str]:
    match = re.search(r'<div class="vBsp[^"]*">(.*?)</div>', html, re.S)
    if not match:
        return []

    examples = []
    for item in re.findall(r"<li[^>]*>(.*?)</li>", match.group(1), re.S):
        text = _clean_html(re.sub(r"<a\b.*?</a>", "", item, flags=re.S))
        if text:
            examples.append(text)

    return examples


def _first_meta_content(name: str, html: str) -> str | None:
    match = re.search(
        rf'<meta\s+name="{re.escape(name)}"\s+content="([^"]*)"',
        html,
        re.I,
    )
    return unescape(match.group(1)).strip() if match else None


def _first_text(pattern: str, html: str) -> str | None:
    match = re.search(pattern, html, re.S | re.I)
    return _clean_html(match.group(1)) if match else None


def _clean_html(value: str) -> str:
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    value = unescape(value)
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse verbformen.com data for a German word.")
    parser.add_argument("word", nargs="?", default="gehen", help="German word, for example: gehen")
    args = parser.parse_args()

    entry = parse_verbformen(args.word)
    print(json.dumps(entry.to_dict(), ensure_ascii=False, indent=2))
