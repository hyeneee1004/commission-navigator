# -*- coding: utf-8 -*-
import streamlit as st

import ui
from portal_data import QUIZ

st.set_page_config(page_title="OX 퀴즈 — 수수료 내비게이터", page_icon="🧭", layout="centered",
                   initial_sidebar_state="collapsed")
ui.inject()
ui.tabbar("quiz")
ui.page_head("✏️ 나, 규정 얼마나 알까?",
             "5문항 O/X. 다 맞히면 환수 걱정 절반은 던 겁니다.",
             mood="happy", say="가볍게 5문제! 저랑 같이 풀어봐요 ✊")

if "quiz_ans" not in st.session_state:
    st.session_state.quiz_ans = {}

st.write("")
for i, item in enumerate(QUIZ):
    with st.container(border=True):
        st.markdown(f"**Q{i + 1}. {item['q']}**")
        picked = st.session_state.quiz_ans.get(i)
        if picked is None:
            c1, c2 = st.columns(2)
            if c1.button("⭕ 맞다", key=f"o{i}", use_container_width=True):
                st.session_state.quiz_ans[i] = True
                st.rerun()
            if c2.button("❌ 아니다", key=f"x{i}", use_container_width=True):
                st.session_state.quiz_ans[i] = False
                st.rerun()
        else:
            ok = picked == item["a"]
            (st.success if ok else st.error)(
                f"**{'🎯 정답!' if ok else '😅 오답'}** (정답: {'O' if item['a'] else 'X'}) — {item['e']}"
            )

answered = len(st.session_state.quiz_ans)
if answered == len(QUIZ):
    correct = sum(1 for i, item in enumerate(QUIZ) if st.session_state.quiz_ans[i] == item["a"])
    st.write("")
    if correct == len(QUIZ):
        ui.speak("happy", "규정 마스터! 지점에 자랑하셔도 됩니다.",
                 tone="bb-safe", big=f"🏆 만점 — {correct} / {len(QUIZ)}")
        st.balloons()
    elif correct >= 3:
        ui.speak("think", "아쉬운 문항의 키워드를 [규정 찾기]에서 다시 확인해 보세요.",
                 tone="bb-amber", big=f"👍 점수 {correct} / {len(QUIZ)}")
    else:
        ui.speak("sad", "환수 위험이 있어요! 해설을 읽고 [규정 찾기]에서 복습해요.",
                 tone="bb-warn", big=f"📚 점수 {correct} / {len(QUIZ)}")
    lb1, lb2 = st.columns(2)
    lb1.page_link("pages/1_규제_검색.py", label="🔎 규정 찾기에서 복습하기", use_container_width=True)
    if lb2.button("다시 풀기", use_container_width=True):
        st.session_state.quiz_ans = {}
        st.rerun()
else:
    st.progress(answered / len(QUIZ), text=f"진행 {answered} / {len(QUIZ)}")
