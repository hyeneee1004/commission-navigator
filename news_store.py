# -*- coding: utf-8 -*-
"""개편 관련 최근 뉴스 — 구글 뉴스 RSS 수집 (API 키 불필요, 30분 캐시).

공개 정보만 다루므로 내부판·공개판 공용.
"""
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import streamlit as st

QUERIES = [
    "보험 판매수수료 개편",
    "GA 1200% 룰",
    "보험 수수료 분급",
    "보험 차익거래 환수",
]


def _safe_xml(data: bytes):
    """XXE·billion-laughs 방지 — 엔티티·DOCTYPE 선언이 있는 피드는 거부."""
    head = data[:2048].upper()
    if b"<!DOCTYPE" in head or b"<!ENTITY" in head:
        raise ValueError("unsafe XML feed")
    return ET.fromstring(data)


def _fetch_one(query: str):
    q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    root = _safe_xml(urllib.request.urlopen(req, timeout=10).read())
    out = []
    for it in root.findall(".//item"):
        title = it.findtext("title") or ""
        src = title.rsplit(" - ", 1)[-1] if " - " in title else ""
        head = title.rsplit(" - ", 1)[0] if " - " in title else title
        try:
            dt = parsedate_to_datetime(it.findtext("pubDate"))
        except Exception:
            continue
        out.append(dict(title=head.strip(), source=src.strip(),
                        link=it.findtext("link") or "", date=dt))
    return out


@st.cache_data(ttl=1800, show_spinner="최근 뉴스 불러오는 중…")
def fetch_news(limit: int = 8):
    """여러 검색어 결과를 합쳐 최신순 상위 limit건. 실패 시 빈 목록."""
    seen, items = set(), []
    for q in QUERIES:
        try:
            for a in _fetch_one(q):
                key = a["title"][:30]
                if key in seen:
                    continue
                seen.add(key)
                items.append(a)
        except Exception:
            continue
    items.sort(key=lambda a: a["date"], reverse=True)
    return items[:limit]


# ── 검색어로 뉴스 본문 발췌 (규정찾기 연동) ──
import re
from html import unescape

_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def _get(url: str, timeout: int = 8, max_bytes: int = 800_000):
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(max_bytes), r.geturl()


def _bing_search(query: str):
    """Bing 뉴스 RSS 검색 — 링크의 url= 파라미터가 기사 원문 주소 (직접 접근 가능)."""
    q = urllib.parse.quote(query)
    rss = f"https://www.bing.com/news/search?q={q}&format=rss&setmkt=ko-KR"
    data, _ = _get(rss, timeout=10)
    out = []
    for it in _safe_xml(data).findall(".//item"):
        link = it.findtext("link") or ""
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
        real = qs.get("url", [link])[0]
        try:
            dt = parsedate_to_datetime(it.findtext("pubDate"))
        except Exception:
            continue
        host = urllib.parse.urlparse(real).netloc.replace("www.", "")
        out.append(dict(title=(it.findtext("title") or "").strip(),
                        source=host, link=real, date=dt))
    return out


def _html_text(data: bytes) -> str:
    """기사 HTML → 본문 텍스트 (대충이지만 발췌엔 충분)."""
    head = data[:4000].decode("ascii", "ignore").lower()
    m = re.search(r'charset=["\']?([a-z0-9_-]+)', head)
    enc = m.group(1) if m else "utf-8"
    try:
        html = data.decode(enc, "replace")
    except LookupError:
        html = data.decode("utf-8", "replace")
    html = re.sub(r"(?is)<(script|style|noscript|header|footer|nav|aside)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", unescape(html)).strip()


@st.cache_data(ttl=1800, show_spinner=False)
def news_excerpts(query: str, limit: int = 3):
    """검색어로 뉴스를 찾아 기사 본문에서 해당 단어 주변을 발췌.

    반환: [{title, source, date, url, snippets[≤2]}] — 본문 수집 실패 시
    제목에 검색어가 있는 기사만 snippets 없이 포함.
    """
    query = query.strip()
    if not query:
        return []
    try:
        arts = _bing_search(query)[:6]
    except Exception:
        arts = []
    hits = []
    for a in arts:
        if len(hits) >= limit:
            break
        snips = []
        try:
            data, final = _get(a["link"])
            text = _html_text(data)
            low, ql = text.lower(), query.lower()
            cands, pos = [], 0
            while len(cands) < 6:
                i = low.find(ql, pos)
                if i < 0:
                    break
                s, e = max(0, i - 90), min(len(text), i + len(query) + 90)
                frag = (text[s:i] + "**" + text[i:i + len(query)] + "**"
                        + text[i + len(query):e]).strip()
                cands.append(("…" if s > 0 else "") + frag + ("…" if e < len(text) else ""))
                pos = i + len(query) + 180
            junk = ("Internet Explorer", "브라우저", "기사보기", "로그인", "회원가입",
                    "구독", "바로가기", "페이스북", "인스타그램", "유튜브", "-->")
            clean = [c for c in cands if not any(j in c for j in junk)]
            snips = (clean or cands)[:2]
        except Exception:
            pass
        if snips or query.lower() in a["title"].lower():
            hits.append(dict(title=a["title"], source=a["source"], date=a["date"],
                             url=a["link"], snippets=snips))
    if hits:
        return hits
    try:    # Bing 0건이면 구글 뉴스 제목 검색으로 보조 (본문 발췌 없음)
        for a in _fetch_one(query)[:limit]:
            if query.lower() in a["title"].lower():
                hits.append(dict(title=a["title"], source=a["source"], date=a["date"],
                                 url=a["link"], snippets=[]))
    except Exception:
        pass
    return hits
