# -*- coding: utf-8 -*-
from datetime import date

import streamlit as st

import ui
from portal_data import COST_MATRIX

st.set_page_config(page_title="수수료 내비게이터", page_icon="🧭", layout="wide",
                   initial_sidebar_state="collapsed")
ui.inject()
ui.tabbar("index")
ui.page_head("수수료 내비게이터",
             "2026 판매수수료 개편 — 어렵게 읽을 필요 없이, 딱 3가지만 기억하세요.",
             mood="hello", say="안녕하세요! 바뀌는 수수료 제도, 제가 쉽게 알려드릴게요 🙌")

# ── ① 핵심 3가지 ──
st.markdown("### ① 딱 3가지만 기억하세요")
c1, c2, c3 = st.columns(3, gap="medium")
with c1:
    ui.p_card("pc-peach", "26년 3월부터 · 시행 중", "3년 안에 깨지면, 받은 돈 도로 냅니다",
              "수수료+해약환급금이 고객 납입보험료보다 크면 <b>차익거래</b> → 환수. "
              "실효(미납)도 포함돼요.", "감독규정 제4-32조 제6항")
with c2:
    ui.p_card("pc-lavender", "26년 7월부터 · 시행 중", "첫해 받을 수 있는 돈 = 1년치 보험료까지",
              "<b>1,200% 룰</b>. 계약 1건 단위로 따지고, 지점 운영비·시상금까지 전부 포함됩니다.",
              "감독규정 제4-32조 제5항")
with c3:
    ui.p_card("pc-sky", "27년 1월부터 · 예정", "한 번에 받던 수수료, 4~7년 나눠 받습니다",
              "<b>분급 제도</b>. 첫해 수령액은 줄지만, 계약이 오래 유지되면 총액은 더 많아져요.",
              "감독규정 제4-32조 제11~13항")

# ── ② 개편 타임라인 (오늘 위치 표시) ──
st.write("")
TL_START, TL_END = date(2026, 3, 1), date(2029, 1, 1)
today = date.today()
pct = max(0.0, min(100.0, (today - TL_START).days / (TL_END - TL_START).days * 100))
MILES = [
    (date(2026, 3, 1), "차익거래 금지", "비교공시 시작"),
    (date(2026, 7, 1), "1,200% 룰", "비교설명의무"),
    (date(2027, 1, 1), "4년 분급", "선지급 한도"),
    (date(2029, 1, 1), "7년 분급", "장기유지수수료"),
]
d_next = next(((m[0] - today).days, m[1]) for m in MILES if m[0] > today)
st.markdown(f"### ② 지금 어디까지 왔나 — 다음 변화 「{d_next[1]}」까지 "
            f"<span style='color:#FF5D5D;font-size:1.4rem'>D-{d_next[0]}</span>",
            unsafe_allow_html=True)

nodes = ""
for md, title, sub in MILES:
    p = max(0.0, min(100.0, (md - TL_START).days / (TL_END - TL_START).days * 100))
    passed = md <= today
    dot = ("background:#2BC48A;border:3px solid #2BC48A;color:#fff;" if passed
           else "background:#FFFFFF;border:3px solid #3D6BFF;color:#3D6BFF;")
    badge = ('<span style="color:#2BC48A;font-weight:800;font-size:.85rem">✓ 시행 중</span>' if passed
             else f'<span style="color:#FF5D5D;font-weight:800;font-size:.85rem">D-{(md - today).days}</span>')
    nodes += (
        f'<div style="position:absolute;left:{p}%;top:26px;transform:translateX(-50%);text-align:center;width:150px">'
        f'<div style="width:22px;height:22px;border-radius:50%;{dot}margin:0 auto;'
        f'display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:800">'
        f'{"✓" if passed else ""}</div>'
        f'<div style="font-size:1.05rem;font-weight:800;color:#26324A;margin-top:8px">{md.year % 100}.{md.month}</div>'
        f'<div style="font-size:.9rem;font-weight:700;color:#3A4560">{title}</div>'
        f'<div style="font-size:.8rem;color:#9AA5B8">{sub}</div>{badge}</div>')

st.markdown(f"""
<div style="position:relative;height:170px;margin:26px 48px 6px">
  <div style="position:absolute;top:34px;left:0;right:0;height:8px;background:#EEF2FA;border-radius:4px"></div>
  <div style="position:absolute;top:34px;left:0;width:{pct}%;height:8px;
       background:linear-gradient(90deg,#2BC48A,#3D6BFF);border-radius:4px"></div>
  <div style="position:absolute;left:{pct}%;top:-8px;transform:translateX(-50%);text-align:center;z-index:2">
    <div style="background:#E39A00;color:#fff;font-weight:800;font-size:.82rem;
         border-radius:99px;padding:2px 12px;white-space:nowrap">📍 오늘 {today.year % 100}.{today.month}.{today.day}</div>
    <div style="width:3px;height:30px;background:#E39A00;margin:2px auto 0"></div>
  </div>
  {nodes}
</div>
<div style="text-align:center;color:#6E7A94;font-weight:700;font-size:.95rem;margin-bottom:4px">
  개편 여정의 <span style="color:#E39A00;font-size:1.15rem;font-weight:800">{pct:.0f}%</span> 지점을 지나고 있어요
</div>
""", unsafe_allow_html=True)

# ── ③ 바로가기 ──
st.write("")
st.markdown("### ③ 지금 확인해 보세요")
g1, g2, g3 = st.columns(3, gap="medium")
with g1:
    ui.p_card("pc-peach", "계약 진단", "이 계약, 해지되면 환수될까?",
              "상품·계약일만 넣으면 예상 환급금과 <b>환수 위험 구간</b>을 진단해요.")
    if st.button("🩺 계약 진단 하러 가기", type="primary", use_container_width=True):
        st.switch_page("pages/3_차익거래_체크.py")
with g2:
    ui.p_card("pc-mint", "소득 계산", "내 소득, 개편 후 얼마나 달라질까?",
              "실제 수수료 규정 기준으로 <b>'27년·'29년 첫해 소득</b>과 필요 실적을 계산해요.")
    if st.button("💰 소득 계산 하러 가기", type="primary", use_container_width=True):
        st.switch_page("pages/2_소득_시뮬레이터.py")
with g3:
    ui.p_card("pc-lavender", "규정 찾기", "궁금한 규정, 한 줄로 확인",
              "먹튀·천이백·가불… 평소 쓰는 말로 검색하면 <b>원문까지</b> 찾아줘요.")
    if st.button("🔎 규정 찾기 하러 가기", type="primary", use_container_width=True):
        st.switch_page("pages/1_규제_검색.py")


# ── ④ 개편 최근 뉴스 ──
st.write("")
st.markdown("### ④ 개편 소식, 뉴스로 확인하세요")
import news_store

news = news_store.fetch_news(8)
if news:
    nc1, nc2 = st.columns(2, gap="medium")
    for i, a in enumerate(news):
        with (nc1 if i % 2 == 0 else nc2):
            st.markdown(
                f'''<a href="{a["link"]}" target="_blank" style="text-decoration:none">
                <div style="background:#FFFFFF;border-radius:16px;padding:14px 18px;margin-bottom:10px;
                     box-shadow:0 4px 12px rgba(61,107,255,.07)">
                <div style="font-size:.95rem;font-weight:700;color:#26324A;line-height:1.45">{a["title"]}</div>
                <div style="font-size:.8rem;color:#9AA5B8;font-weight:600;margin-top:5px">
                {a["source"]} · {a["date"].strftime("%m월 %d일")}</div></div></a>''',
                unsafe_allow_html=True)
    st.caption("출처: 구글 뉴스 검색(판매수수료 개편·1,200% 룰·분급·차익거래) · 30분마다 자동 갱신 · 제목을 누르면 기사로 이동")
else:
    st.caption("뉴스를 불러오지 못했습니다. 네트워크 상태를 확인해 주세요.")

# ── ⑤ 판정표 ──
@st.dialog("비용 분류 판정표 — 뭐가 포함되고 뭐가 빠지나", width="large")
def show_matrix():
    st.caption("출처: GA비용분류 및 처리기준. '포함'이면 1,200% 한도에 합산되는 비용입니다.")

    def _color(v):
        if v in ("포함", "합산"):
            return "background-color:#FFF0F0;color:#FF5D5D;font-weight:800"
        if v in ("제외", "예외"):
            return "background-color:#EAFBF4;color:#2BC48A;font-weight:800"
        if v == "조건부":
            return "background-color:#FFF7E6;color:#E39A00;font-weight:800"
        return ""

    st.dataframe(COST_MATRIX.style.map(_color, subset=["수수료등", "1,200%", "차익거래"]),
                 use_container_width=True, hide_index=True, height=420)


st.write("")
ui.tip("지점 운영비·시상·교육비… 어떤 게 1,200% 한도를 갉아먹는지 헷갈리면 <b>판정표</b>를 열어보세요!")
bc1, _ = st.columns([1.3, 2.7])
if bc1.button("📋 비용 분류 판정표 열기", type="primary", use_container_width=True):
    show_matrix()

st.divider()
st.caption("근거: 금융위·금감원 FAQ 및 개편 관련 배포자료 종합. 본 화면은 안내용이며 법적 근거가 될 수 없습니다.")
