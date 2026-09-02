# -*- coding: utf-8 -*-
"""공통 UI — 시원스쿨풍 에듀테크 스타일.

아주 밝은 블루 배경 + 떠 있는 둥근 흰 카드 + 비비드 블루 단일 포인트 + 알약 탭 + 그라데이션 히어로.
마스코트는 assets/character/01_default~ 규칙 자동 연결.
mood: hello(인사) · warn(경고) · safe(안심) · think(생각) · happy(축하) · sad(아쉬움) · tip(팁)

팔레트: 잉크 #26324A · 블루 #3D6BFF · 그레이 #6E7A94 · 골드 #E39A00
        레드 #FF5D5D · 그린 #2BC48A · 바탕 #F3F6FC
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

BLUE = "#3D6BFF"
# (key, label, url, icon) — 하단 내비 순서: 홈 가운데
PAGES = [
    ("search", "규정 찾기", "/규제_검색", "🔎"),
    ("sim", "소득 계산", "/소득_시뮬레이터", "💰"),
    ("index", "홈", "/", "🏠"),
    ("risk", "계약 진단", "/차익거래_체크", "🩺"),
    ("quiz", "OX 퀴즈", "/OX_퀴즈", "✏️"),
]

CSS = """
<style>
/* ── 골격: 밝은 블루 배경, 카드가 떠 있는 구조 ── */
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display:none !important; }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stAppViewContainer"] {
  background:linear-gradient(180deg,#E9F0FF 0%,#F3F6FC 260px,#F3F6FC 100%); }
.block-container { background:transparent; padding:1.2rem 2.6rem 7rem !important;
  max-width:1150px; }
html, body, [data-testid="stAppViewContainer"] { font-size:16.5px; color:#26324A; }
h1,h2 { color:#26324A; letter-spacing:-0.02em; font-weight:800 !important; }
h3 { color:#26324A; letter-spacing:-0.01em; font-weight:800 !important; font-size:1.18rem !important; }

/* ── 상단 브랜드 헤더 ── */
.brand { display:flex; align-items:center; gap:12px; padding:12px 4px 14px;
  max-width:1150px; margin:0 auto; }
.brand img { height:42px; }
.brand .logo-txt { font-style:italic; font-weight:900; font-size:1.7rem; color:#1F3480;
  letter-spacing:-0.05em; line-height:1; }
.brand .nm { font-weight:800; font-size:1.0rem; color:#1F3480; line-height:1.25; }
.brand .sl { font-size:.75rem; color:#6E7A94; font-weight:600; line-height:1.2; }

/* ── 하단 고정 내비게이션 ── */
.bottomnav { position:fixed; bottom:0; left:0; right:0; z-index:9999;
  background:#FFFFFF; border-top:1px solid #E6ECF7;
  box-shadow:0 -6px 20px rgba(61,107,255,.10);
  display:flex; justify-content:center; gap:6px;
  padding:8px 8px calc(10px + env(safe-area-inset-bottom)); }
.bottomnav a { text-decoration:none; display:flex; flex-direction:column; align-items:center;
  gap:3px; color:#9AA5B8; font-size:.74rem; font-weight:700;
  min-width:74px; padding:4px 10px; border-radius:14px; }
.bottomnav a .ic { font-size:1.35rem; line-height:1; filter:grayscale(1) opacity(.5); }
.bottomnav a:hover { color:#3D6BFF; background:#F3F7FF; }
.bottomnav a.on { color:#3D6BFF; font-weight:800; }
.bottomnav a.on .ic { filter:none; transform:scale(1.12); }

/* ── 히어로 (그라데이션 카드) ── */
.page-head { background:linear-gradient(120deg,#DCE9FF 0%,#E9EDFF 55%,#F7F1FF 100%);
  border-radius:26px; padding:26px 32px; margin-bottom:22px;
  display:flex; justify-content:space-between; align-items:center; gap:24px; }
.page-head .t { font-size:1.75rem; font-weight:800; margin:0 0 6px; letter-spacing:-0.03em; color:#26324A;}
.page-head .n { font-size:.98rem; color:#5B6780; margin:0; line-height:1.6; }
.page-head .n b { color:#3D6BFF; }

/* ── 마스코트 + 말풍선 ── */
.chr-row { display:flex; align-items:center; gap:18px; margin:12px 0 8px; }
.chr { flex:0 0 auto; width:300px; height:300px; border-radius:32px;
  display:flex; align-items:center; justify-content:center; font-size:8rem;
  background:#FFFFFF; box-shadow:0 6px 18px rgba(61,107,255,.08); }
.chr.small { width:180px; height:180px; font-size:4.8rem; border-radius:26px;
  background:transparent; box-shadow:none; }
.chr.hero { width:130px !important; height:130px !important; font-size:3rem; }
.chr img { width:100%; height:100%; object-fit:contain; }
.chr.real { background:transparent; box-shadow:none; }
.bubble { position:relative; background:var(--bb,#FFFFFF); border-radius:20px;
  min-width:220px;
  padding:18px 24px; font-size:1.05rem; line-height:1.65; font-weight:600; color:#26324A;
  flex:1; box-shadow:0 6px 18px rgba(61,107,255,.08); }
.bubble::before { content:""; position:absolute; left:-11px; top:50%; transform:translateY(-50%);
  border:11px solid transparent; border-right-color:var(--bb,#FFFFFF); border-left:none; }
.bubble small { display:block; font-weight:500; color:#6E7A94; font-size:.93rem; margin-top:6px; }
.bubble .big { font-size:1.45rem; font-weight:800; letter-spacing:-0.02em; }
.bb-warn { --bb:#FFF0F0; } .bb-warn .big{color:#FF5D5D;}
.bb-safe { --bb:#EAFBF4; } .bb-safe .big{color:#17A874;}
.bb-amber{ --bb:#FFF7E6; } .bb-amber .big{color:#E39A00;}
.bb-blue { --bb:#FFFFFF; } .bb-blue .big{color:#3D6BFF;}

/* ── 떠 있는 흰 카드 ── */
.p-card { border-radius:22px; padding:22px 24px; height:100%; background:#FFFFFF;
  box-shadow:0 6px 18px rgba(61,107,255,.08); border:none; }
.p-card .tag { display:inline-block; font-size:.8rem; font-weight:800; color:var(--pt,#3D6BFF);
  background:var(--pc,#EAF0FF); border-radius:999px; padding:4px 14px; margin-bottom:12px; }
.p-card .h { font-size:1.22rem; font-weight:800; margin:0 0 8px; line-height:1.45; color:#26324A;}
.p-card .b { font-size:.95rem; color:#5B6780; margin:0; line-height:1.65; }
.p-card .b b { color:var(--pt); }
.p-card .art { display:inline-block; margin-top:12px; font-size:.8rem; color:#6E7A94;
  background:#F3F6FC; border-radius:999px; padding:3px 12px; font-weight:700; }
.pc-sky { --pc:#EAF0FF; --pt:#3D6BFF; }
.pc-mint { --pc:#EAFBF4; --pt:#17A874; }
.pc-peach { --pc:#FFF0F0; --pt:#FF5D5D; }
.pc-lavender { --pc:#FFF7E6; --pt:#E39A00; }
.pc-lemon { --pc:#F1F4FA; --pt:#6E7A94; }

/* ── 큰 숫자 카드 ── */
.stat { border-radius:22px; padding:22px 24px; text-align:center; background:#FFFFFF;
  box-shadow:0 6px 18px rgba(61,107,255,.08); border:none; }
.stat .v { font-size:2.4rem; font-weight:800; letter-spacing:-0.03em; line-height:1.15;
  font-variant-numeric:tabular-nums; color:var(--pt,#3D6BFF); }
.stat .l { font-size:.98rem; font-weight:800; color:#3A4560; margin-top:6px; }
.stat .d { font-size:.9rem; font-weight:600; color:#9AA5B8; margin-top:2px; }

/* ── 로드맵 스텝 ── */
.step { border-radius:22px; padding:20px 22px; height:100%; background:#FFFFFF;
  box-shadow:0 6px 18px rgba(61,107,255,.08); border:none; }
.step .y { font-size:1.5rem; font-weight:800; color:var(--pt,#3D6BFF); letter-spacing:-0.02em;}
.step .w { font-size:.98rem; font-weight:700; margin-top:6px; line-height:1.5; color:#26324A;}
.step .tm { font-size:.84rem; color:#9AA5B8; margin-top:9px; font-weight:600; }

/* ── 모바일 보정 ── */
@media (max-width: 640px) {
  .block-container { padding:.6rem .9rem 6.5rem !important; }
  .tabbar { gap:5px; padding:2px 0 12px; }
  .tabbar a { padding:7px 14px; font-size:.85rem; }
  .page-head { flex-direction:column; align-items:stretch; gap:10px; padding:18px 18px;
    border-radius:20px; }
  .page-head .t { font-size:1.35rem; }
  .page-head .n { font-size:.9rem; }
  .chr { width:150px; height:150px; font-size:4.2rem; }
  .chr.small { width:92px; height:92px; font-size:2.6rem; }
  .chr.hero { width:76px !important; height:76px !important; }
  .chr-row { gap:10px; }
  .bubble { padding:12px 14px; font-size:.95rem; }
  .bubble .big { font-size:1.15rem; }
  .p-card { padding:16px 16px; }
  .p-card .h { font-size:1.05rem; }
  .stat .v { font-size:1.8rem; }
  .step .y { font-size:1.25rem; }
}

/* ── 위젯 교정: 둥근 블루 CTA ── */
div.stButton > button { border-radius:14px; font-weight:700; font-size:.98rem;
  border:1px solid #E6ECF7; color:#3A4560; background:#FFFFFF; padding:.6rem 1.1rem;
  box-shadow:0 2px 8px rgba(61,107,255,.07); }
div.stButton > button:hover { color:#3D6BFF; border-color:#C5D4FF; background:#F7FAFF; }
div.stButton > button:active { transform:translateY(1px); box-shadow:none; }
div.stButton > button[kind="primary"] { background:#3D6BFF; color:#fff; border-color:#3D6BFF;
  font-weight:800; box-shadow:0 6px 16px rgba(61,107,255,.3); }
div.stButton > button[kind="primary"]:hover { background:#2F5BEB; color:#fff; }
[data-testid="stExpander"] details { border-radius:18px; border:1px solid #E6ECF7;
  background:#FFFFFF; }
[data-testid="stDialog"] div[role="dialog"] { border-radius:24px; }
[data-testid="stDataFrame"] { font-size:.95rem; }
div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stVerticalBlock"] { gap:.6rem; }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius:22px !important;
  border-color:#E6ECF7 !important; background:#FFFFFF;
  box-shadow:0 6px 18px rgba(61,107,255,.08); }
hr { border-color:#E6ECF7; }
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
    """상단: 인카 브랜드 헤더 / 하단: 고정 앱 내비게이션."""
    logo = Path(__file__).parent / "assets" / "incar_logo.png"
    if logo.exists():
        mark = f'<img src="data:image/png;base64,{_img_b64(str(logo))}" alt="인카금융서비스">'
    else:
        mark = '<span class="logo-txt">iNCAR</span>'
    st.markdown(
        f'<div class="brand">{mark}<div><div class="sl">인생의 카운슬러</div>'
        f'<div class="nm">인카금융서비스(주) · 수수료 내비게이터</div></div></div>',
        unsafe_allow_html=True)
    links = []
    for key, label, url, icon in PAGES:
        cls = "on" if key == active else ""
        links.append(f'<a class="{cls}" href="{url}" target="_self">'
                     f'<span class="ic">{icon}</span>{label}</a>')
    st.markdown(f'<div class="bottomnav">{"".join(links)}</div>', unsafe_allow_html=True)


def page_head(title: str, note: str, mood: str = "hello", say: str = ""):
    if IS_PUBLIC:
        note += ' <span style="background:#FFF7E6;color:#E39A00;border-radius:999px;padding:2px 12px;font-weight:800;font-size:.82rem">공개판 · 예시값 기준</span>'
    bubble = ""
    if say:
        hero_chr = _chr_html(mood, small=True).replace('chr small', 'chr small hero')
        bubble = (f'<div class="chr-row" style="max-width:560px;margin:0">{hero_chr}'
                  f'<div class="bubble bb-blue" style="font-size:.97rem;padding:13px 17px">{say}</div></div>')
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
        f'<div class="bubble bb-amber" style="font-size:.95rem;padding:13px 17px">{text}</div></div>',
        unsafe_allow_html=True)


def p_card(theme: str, tag: str, head: str, body: str, art: str = "", badge: bool = False):
    art_html = f'<span class="art">{art}</span>' if art else ""
    b_html = ('<span style="position:absolute;top:-12px;right:16px;background:#E39A00;color:#fff;'
              'font-size:.76rem;font-weight:800;border-radius:999px;padding:4px 14px;'
              'box-shadow:0 4px 10px rgba(227,154,0,.3)">🌟 내게 맞는 전략</span>'
              ) if badge else ""
    extra = ("position:relative;box-shadow:0 6px 18px rgba(61,107,255,.16);"
             "outline:2px solid var(--pt);" if badge else "position:relative;")
    st.markdown(
        f'<div class="p-card {theme}" style="{extra}">{b_html}<span class="tag">{tag}</span>'
        f'<p class="h">{head}</p><p class="b">{body}</p>{art_html}</div>', unsafe_allow_html=True)


def stat(theme: str, value: str, label: str, desc: str = ""):
    st.markdown(
        f'<div class="stat {theme}"><div class="v">{value}</div>'
        f'<div class="l">{label}</div><div class="d">{desc}</div></div>', unsafe_allow_html=True)


def step(theme: str, year: str, what: str, tm: str):
    st.markdown(
        f'<div class="step {theme}"><div class="y">{year}</div>'
        f'<div class="w">{what}</div><div class="tm">{tm}</div></div>', unsafe_allow_html=True)
