# -*- coding: utf-8 -*-
"""공통 UI — 미드나잇 네이비 톤온톤(C) + 골드 포인트·버건디 경고(A) 콘셉트.

상단 INDEX 포스트잇 탭(네이비 톤온톤). 마스코트는 assets/character/01_default~ 규칙 자동 연결.
mood: hello(인사) · warn(경고) · safe(안심) · think(생각) · happy(축하) · sad(아쉬움) · tip(팁)

팔레트: 잉크 #152238 · 네이비 #2456A6 · 스틸 #4A6FA5 · 골드 #B08D2F(#C08A00 텍스트)
        버건디 #CE3B3B · 세이지그린 #17A673 · 바탕 #E9EDF3
"""
import base64
from pathlib import Path

import streamlit as st

IS_PUBLIC = (Path(__file__).parent / "PUBLIC.flag").exists()
ASSET_DIR = Path(__file__).parent / "assets" / "character"

MOOD_FILE = {
    "hello": "02_smile.png",
    "warn": "04_surprise.png",
    "safe": "08_love.png",
    "think": "09_thinking.png",
    "happy": "03_cheer.png",
    "sad": "06_sad.png",
    "tip": "07_wink.png",
}
DEFAULT_FILE = "01_default.png"

MOOD_FALLBACK = {"hello": "🐥", "warn": "🚨", "safe": "😊", "think": "🤔",
                 "happy": "🎉", "sad": "😢", "tip": "💡"}

# (key, label, url, 탭 색) — 톤온톤: 전 탭 네이비 통일
NAVY = "#2456A6"
PAGES = [
    ("index", "홈", "/", NAVY),
    ("search", "규정 찾기", "/규제_검색", NAVY),
    ("sim", "소득 계산", "/소득_시뮬레이터", NAVY),
    ("risk", "계약 진단", "/차익거래_체크", NAVY),
    ("quiz", "OX 퀴즈", "/OX_퀴즈", NAVY),
]

CSS = """
<style>
/* ── 골격: 쿨 블루 바탕 + 화이트 패널 ── */
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display:none !important; }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stAppViewContainer"] { background:#E9EDF3; }
.block-container { background:#FFFFFF; border-radius:18px;
  padding:2.2rem 3rem 3rem !important; max-width:1180px; margin-top:.2rem;
  box-shadow:0 2px 14px rgba(21,34,56,.08); }
html, body, [data-testid="stAppViewContainer"] { font-size:17px; color:#152238; }
h1,h2,h3 { color:#152238; letter-spacing:-0.02em; font-weight:800 !important; }

/* ── INDEX 탭: 포스트잇, 네이비 톤온톤 ── */
.tabbar { display:flex; gap:7px; align-items:flex-end; padding:10px 6px 0; margin:0 auto 20px;
  max-width:1180px; overflow-x:auto; border-bottom:3px solid #2456A6; }
.tabbar .idx { font-size:.74rem; letter-spacing:.24em; color:#8A99AF; margin-right:8px;
  font-weight:800; align-self:center; }
.tabbar a { white-space:nowrap; text-decoration:none; font-weight:800; font-size:.98rem;
  padding:9px 22px 7px; border-radius:9px 9px 0 0; position:relative;
  background:#DCE4EF; color:#4A6FA5; border:1px solid #C4D0E0; border-bottom:none;
  box-shadow:inset 0 -9px 10px -10px rgba(21,34,56,.4); }
.tabbar a:hover { background:#E8EDF4; color:#2456A6; padding-top:11px; }
.tabbar a.on { background:#2456A6; color:#FFFFFF; padding:13px 24px 8px;
  border-color:#2456A6; box-shadow:0 -2px 8px rgba(27,58,107,.3); }

/* ── 페이지 머리 ── */
.page-head { display:flex; justify-content:space-between; align-items:center; gap:24px;
  padding-bottom:14px; margin-bottom:6px; border-bottom:2px solid #E8EDF4; }
.page-head .t { font-size:2.0rem; font-weight:800; margin:0 0 6px; letter-spacing:-0.03em;}
.page-head .n { font-size:1.0rem; color:#4A6FA5; margin:0; line-height:1.6; }
.page-head .n b { color:#CE3B3B; }

/* ── 마스코트 + 말풍선 ── */
.chr-row { display:flex; align-items:center; gap:20px; margin:14px 0 10px; }
.chr { flex:0 0 auto; width:215px; height:215px; border-radius:24px;
  display:flex; align-items:center; justify-content:center; font-size:6rem;
  background:#EEF2F7; }
.chr.small { width:130px; height:130px; font-size:3.6rem; border-radius:18px; }
.chr img { width:100%; height:100%; object-fit:contain; }
.chr.real { background:transparent; }
.bubble { position:relative; background:var(--bb,#E8EDF4); border-radius:16px;
  padding:20px 26px; font-size:1.12rem; line-height:1.65; font-weight:600; color:#152238;
  flex:1; }
.bubble::before { content:""; position:absolute; left:-12px; top:50%; transform:translateY(-50%);
  border:12px solid transparent; border-right-color:var(--bb,#E8EDF4); border-left:none; }
.bubble small { display:block; font-weight:500; color:#4A6FA5; font-size:.98rem; margin-top:6px; }
.bubble .big { font-size:1.55rem; font-weight:800; letter-spacing:-0.02em; }
.bb-warn { --bb:#FBE9E9; } .bb-warn .big{color:#CE3B3B;}
.bb-safe { --bb:#E2F6EE; } .bb-safe .big{color:#17A673;}
.bb-amber{ --bb:#FCF2D4; } .bb-amber .big{color:#C08A00;}
.bb-blue { --bb:#E8EDF4; } .bb-blue .big{color:#2456A6;}

/* ── 카드: 화이트 + 상단 컬러 보더 (A 구조) ── */
.p-card { border-radius:14px; padding:22px 24px; height:100%; background:#FFFFFF;
  border:1px solid #DFE6EF; border-top:3px solid var(--pt,#2456A6); }
.p-card .tag { display:inline-block; font-size:.83rem; font-weight:800; color:var(--pt,#2456A6);
  background:var(--pc,#E8EDF4); border-radius:7px; padding:3px 12px; margin-bottom:12px;
  letter-spacing:.04em; }
.p-card .h { font-size:1.3rem; font-weight:800; margin:0 0 8px; line-height:1.4; color:#152238;}
.p-card .b { font-size:.98rem; color:#3D4C66; margin:0; line-height:1.65; }
.p-card .b b { color:var(--pt); }
.p-card .art { display:inline-block; margin-top:12px; font-size:.82rem; color:#4A6FA5;
  background:#EEF2F7; border-radius:6px; padding:2px 11px; font-weight:700; }
.pc-sky { --pc:#E8EDF4; --pt:#2456A6; }
.pc-mint { --pc:#E2F6EE; --pt:#17A673; }
.pc-peach { --pc:#FBE9E9; --pt:#CE3B3B; }
.pc-lavender { --pc:#FCF2D4; --pt:#C08A00; }
.pc-lemon { --pc:#E3E9F1; --pt:#4A6FA5; }

/* ── 큰 숫자 ── */
.stat { border-radius:14px; padding:22px 24px; text-align:center; background:#FFFFFF;
  border:1px solid #DFE6EF; border-top:3px solid var(--pt,#2456A6); }
.stat .v { font-size:2.6rem; font-weight:800; letter-spacing:-0.03em; line-height:1.15;
  font-variant-numeric:tabular-nums; color:var(--pt,#2456A6); }
.stat .l { font-size:1.0rem; font-weight:800; color:#3D4C66; margin-top:6px; }
.stat .d { font-size:.92rem; font-weight:600; color:#7183A0; margin-top:2px; }

/* ── 로드맵 스텝 ── */
.step { border-radius:14px; padding:20px 22px; height:100%; background:#FFFFFF;
  border:1px solid #DFE6EF; border-top:3px solid var(--pt,#2456A6); }
.step .y { font-size:1.6rem; font-weight:800; color:var(--pt,#2456A6); letter-spacing:-0.02em;}
.step .w { font-size:1.0rem; font-weight:700; margin-top:6px; line-height:1.5; color:#152238;}
.step .tm { font-size:.86rem; color:#7183A0; margin-top:9px; font-weight:600; }

/* ── 모바일 보정 ── */
@media (max-width: 640px) {
  .block-container { padding:1.1rem 1rem 2rem !important; border-radius:0 0 14px 14px; }
  .tabbar { gap:4px; padding:8px 2px 0; margin-bottom:14px; }
  .tabbar .idx { display:none; }
  .tabbar a { padding:7px 12px 6px; font-size:.86rem; }
  .tabbar a.on { padding:9px 14px 6px; }
  .page-head { flex-direction:column; align-items:stretch; gap:10px; }
  .page-head .t { font-size:1.45rem; }
  .page-head .n { font-size:.92rem; }
  .chr { width:110px; height:110px; font-size:3.2rem; }
  .chr.small { width:64px; height:64px; font-size:2rem; }
  .chr-row { gap:10px; }
  .bubble { padding:12px 14px; font-size:.98rem; }
  .bubble .big { font-size:1.2rem; }
  .p-card { padding:16px 16px; }
  .p-card .h { font-size:1.1rem; }
  .stat .v { font-size:1.9rem; }
  .step .y { font-size:1.3rem; }
}

/* ── 위젯 교정 ── */
div.stButton > button { border-radius:10px; font-weight:800; font-size:1.0rem;
  border:1px solid #C4D0E0; color:#2456A6; background:#FFFFFF; padding:.65rem 1.1rem; }
div.stButton > button:hover { background:#EEF2F7; border-color:#2456A6; }
div.stButton > button[kind="primary"] { background:#2456A6; color:#fff; border-color:#2456A6; }
div.stButton > button[kind="primary"]:hover { background:#1A419E; }
[data-testid="stPageLink-NavLink"] { border:1px solid #C4D0E0; border-radius:10px;
  font-weight:800; color:#2456A6; }
[data-testid="stExpander"] details { border-radius:12px; border:1px solid #DFE6EF; }
[data-testid="stDialog"] div[role="dialog"] { border-radius:16px; }
[data-testid="stDataFrame"] { font-size:.98rem; }
hr { border-color:#DFE6EF; }
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _img_b64(path_str: str) -> str:
    return base64.b64encode(Path(path_str).read_bytes()).decode()


def _chr_html(mood: str, small: bool = False) -> str:
    cls = "chr small" if small else "chr"
    for name in (MOOD_FILE.get(mood, DEFAULT_FILE), DEFAULT_FILE):
        img = ASSET_DIR / name
        if img.exists():
            b64 = _img_b64(str(img))
            return f'<div class="{cls} real"><img src="data:image/png;base64,{b64}" alt="{mood}"></div>'
    return f'<div class="{cls}">{MOOD_FALLBACK.get(mood, "🐥")}</div>'


def tabbar(active: str):
    links = ['<span class="idx">INDEX</span>']
    for key, label, url, _color in PAGES:
        cls = "on" if key == active else ""
        links.append(f'<a class="{cls}" href="{url}" target="_self">{label}</a>')
    st.markdown(f'<div class="tabbar">{"".join(links)}</div>', unsafe_allow_html=True)


def page_head(title: str, note: str, mood: str = "hello", say: str = ""):
    if IS_PUBLIC:
        note += ' <span style="background:#FCF2D4;color:#C08A00;border-radius:6px;padding:1px 10px;font-weight:800;font-size:.85rem">공개판 · 예시값 기준</span>'
    bubble = ""
    if say:
        bubble = (f'<div class="chr-row" style="max-width:520px;margin:0">{_chr_html(mood, small=True)}'
                  f'<div class="bubble bb-blue" style="font-size:1.0rem;padding:14px 18px">{say}</div></div>')
    st.markdown(
        f'<div class="page-head"><div><p class="t">{title}</p><p class="n">{note}</p></div>{bubble}</div>',
        unsafe_allow_html=True)


def speak(mood: str, text: str, sub: str = "", tone: str = "bb-blue", big: str = ""):
    big_html = f'<span class="big">{big}</span><br>' if big else ""
    st.markdown(
        f'<div class="chr-row">{_chr_html(mood)}'
        f'<div class="bubble {tone}">{big_html}{text}'
        f'{f"<small>{sub}</small>" if sub else ""}</div></div>', unsafe_allow_html=True)


def tip(text: str):
    st.markdown(
        f'<div class="chr-row">{_chr_html("tip", small=True)}'
        f'<div class="bubble bb-amber" style="font-size:.98rem;padding:14px 18px">{text}</div></div>',
        unsafe_allow_html=True)


def p_card(theme: str, tag: str, head: str, body: str, art: str = ""):
    art_html = f'<span class="art">{art}</span>' if art else ""
    st.markdown(
        f'<div class="p-card {theme}"><span class="tag">{tag}</span>'
        f'<p class="h">{head}</p><p class="b">{body}</p>{art_html}</div>', unsafe_allow_html=True)


def stat(theme: str, value: str, label: str, desc: str = ""):
    st.markdown(
        f'<div class="stat {theme}"><div class="v">{value}</div>'
        f'<div class="l">{label}</div><div class="d">{desc}</div></div>', unsafe_allow_html=True)


def step(theme: str, year: str, what: str, tm: str):
    st.markdown(
        f'<div class="step {theme}"><div class="y">{year}</div>'
        f'<div class="w">{what}</div><div class="tm">{tm}</div></div>', unsafe_allow_html=True)
