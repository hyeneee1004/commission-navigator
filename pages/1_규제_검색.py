# -*- coding: utf-8 -*-
import streamlit as st

import ui
from portal_data import CARDS

st.set_page_config(page_title="규정 찾기 — 수수료 내비게이터", page_icon="🧭", layout="wide",
                   initial_sidebar_state="collapsed")
ui.inject()
ui.tabbar("search")
ui.page_head("🔎 규정 찾기",
             "평소 쓰는 말(먹튀·천이백·가불…)로 검색하세요. 카드를 누르면 자세한 내용이 열립니다.",
             mood="think", say="궁금한 단어만 치면 제가 관련 규정을 찾아드려요!")

if "query" not in st.session_state:
    st.session_state.query = ""

st.write("")
st.markdown("**① 빠른 검색** — 버튼을 누르거나 검색어를 입력하세요")
chip_cols = st.columns(8)
for col, kw in zip(chip_cols, ["차익거래", "1200", "신인", "분급", "환수", "대여금", "지사", "환급률표"]):
    if col.button(kw, use_container_width=True, key=f"chip_{kw}"):
        st.session_state.query = kw

q = st.text_input("검색", value=st.session_state.query,
                  placeholder="찾을 규정·용어 입력", label_visibility="collapsed")

ql = q.strip().lower()
hits = [c for c in CARDS
        if not ql or ql in (c["title"] + c["summary"] + c["detail"] + c["action"] + c["syn"]).lower()]


@st.dialog("자세히 보기", width="large")
def detail(card):
    st.markdown(f"### {card['title']}")
    st.markdown(f':blue[**{card["art"]}**]')
    st.markdown(f"**요지** — {card['summary']}")
    st.markdown(f"**해설** — {card['detail']}")
    st.info(f"**이렇게 하세요** — {card['action']}", icon="👉")


if not hits:
    ui.speak("sad", f"'{q}'는 못 찾았어요. 위 버튼의 키워드로 다시 검색해 볼까요?", tone="bb-warn")

st.markdown(f"**② 규정 요약 카드** ({len(hits)}건)")
THEMES = ["pc-peach", "pc-lavender", "pc-sky", "pc-mint", "pc-lemon"]
for row_start in range(0, len(hits), 2):
    cols = st.columns(2, gap="medium")
    for col, c in zip(cols, hits[row_start:row_start + 2]):
        n = CARDS.index(c)
        with col:
            ui.p_card(THEMES[n % len(THEMES)], f"규정 {n + 1:02d}", c["title"], c["summary"],
                      c["art"].split("·")[0].strip())
            if st.button("자세히 보기 →", key=f"d_{c['title']}", type="primary"):
                detail(c)
    st.write("")

# ── 참고자료 원문 검색 (NotebookLM 방식: 폴더에 넣으면 자동 반영) ──
import doc_store

if ql:
    doc_hits = doc_store.search_docs(q)
    if doc_hits:
        st.markdown(f"### ③ 참고자료 원문에서 찾기 <small>({len(doc_hits)}건)</small>",
                    unsafe_allow_html=True)
        for h in doc_hits:
            with st.container(border=True):
                st.markdown(f"**📄 {h['file']}** · {h['loc']}")
                st.markdown(f"…{h['snippet']}…")

    # ── 뉴스에서 찾기 — 저장된 규정·자료에 없는 용어도 최신 기사에서 발췌 ──
    import news_store

    with st.spinner("📰 뉴스에서도 찾는 중…"):
        news_hits = news_store.news_excerpts(q)
    if news_hits:
        st.markdown(f"### ④ 뉴스에서 찾기 <small>({len(news_hits)}건)</small>",
                    unsafe_allow_html=True)
        st.caption("뉴스 검색(Bing) 결과 기사 본문에서 발췌한 인용입니다 — 기사 내용은 언론사 견해이며, "
                   "규정 해석은 감독규정 원문·회사 기준이 우선합니다.")
        for h in news_hits:
            with st.container(border=True):
                st.markdown(f"**📰 [{h['title']}]({h['url']})** · "
                            f"{h['source']} · {h['date'].strftime('%Y.%m.%d')}")
                for sn in h["snippets"]:
                    st.markdown(f"> {sn}")
                if not h["snippets"]:
                    st.caption("본문을 불러오지 못했어요 — 제목이 일치해 표시합니다. 제목을 눌러 기사에서 확인하세요.")
    elif not doc_hits and not hits:
        st.caption("📰 뉴스에서도 관련 기사를 찾지 못했어요.")

with st.expander(f"⑤ 📁 자료함 — 참고자료 관리 — 현재 {len(doc_store.doc_files())}개 파일 로딩됨"):
    doc_store.uploader_block(st, doc_store.DOC_DIR,
                             "새 참고자료(PDF·PPTX·XLSX·TXT)를 올리면 저장 후 바로 검색에 포함됩니다",
                             ["pdf", "pptx", "xlsx", "xlsm", "txt", "md"], "up_docs")
    for fname, n_chunks in doc_store.doc_files():
        st.markdown(f"- {fname} <small>({n_chunks}개 구역)</small>", unsafe_allow_html=True)
    if st.button("🔄 새 자료 다시 읽기"):
        doc_store.clear_caches()
        st.rerun()

ui.tip("여기 없는 궁금증은 수수료팀에 문의하세요. 3차 FAQ(분급) 질의도 접수 중입니다 (기한 8/7).")
