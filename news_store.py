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


def _fetch_one(query: str):
    q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    root = ET.fromstring(urllib.request.urlopen(req, timeout=10).read())
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
