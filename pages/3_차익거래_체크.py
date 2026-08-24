# -*- coding: utf-8 -*-
"""계약 진단 — 보험사 해약환급금 예시 화면 응용 + 차익거래·1,200% 규제 진단 통합."""
from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

import doc_store
import ui
from portal_data import DEFAULT_RATE_DIRS, arbitrage_table, load_rate_tables, refund_rate

st.set_page_config(page_title="계약 진단 — 수수료 내비게이터", page_icon="🧭", layout="wide",
                   initial_sidebar_state="collapsed")
ui.inject()
ui.tabbar("risk")
ui.page_head("🩺 계약 진단 — 환급금·환수 위험 한눈에",
             "상품과 계약 정보를 넣으면 예상 해약환급금과 함께 <b>지금 해지되면 얼마가 환수되는지</b>까지 진단합니다.<br>"
             "산식: 수수료등 + 해약환급금 − 환수금 &gt; 납입보험료 (증권번호 단위, 3년 내)",
             mood="warn", say="계약하기 전에 저랑 같이 위험 구간부터 확인해요!")


@st.cache_data(show_spinner="해약환급률표 로딩 중…")
def _load(dirs, _fingerprint):
    return load_rate_tables(list(dirs))


st.write("")
left, right = st.columns([1, 2], gap="large")

# ──────────────── ① 조회부 ────────────────
with left:
    with st.container(border=True):
        st.markdown("**① 계약 조회**")
        policy_no = st.text_input("증권번호 (메모용)", value="", placeholder="예: A123456789",
                                  help="지금은 메모용입니다. 추후 계약 데이터 연동 시 자동조회로 교체 예정.")
        c1, c2 = st.columns(2)
        P = c1.number_input("월 보험료 (만원)", 1.0, 1000.0, 10.0, 1.0)
        fee = c2.number_input("받은(받을) 수수료 (만원)", 0.0, 10000.0, 90.0, 5.0,
                              help="모집수수료+시책 등 초년도 초기 지급분")
        start = st.date_input("계약일자", value=date.today(), max_value=date.today())

        with st.expander("📤 환급률표 업로드·관리"):
            doc_store.uploader_block(st, doc_store.REFUND_DIR,
                                     "보험사 해약환급률표(xlsx)를 올리면 저장 후 바로 반영됩니다",
                                     ["xlsx", "xlsm"], "up_refund")
            if st.button("환급률표 다시 읽기"):
                _load.clear()
                st.rerun()
        rates_df, logs = _load(tuple(DEFAULT_RATE_DIRS),
                               doc_store._sig(doc_store.REFUND_DIR, {".xlsx", ".xlsm"}))
        for line in logs:
            st.caption(line)

        mode = st.radio("환급률", ["상품 선택", "직접 입력"], horizontal=True,
                        index=0 if len(rates_df) else 1)
        prod_label = "직접 입력"
        kind = term = "-"
        comp = "-"
        if mode == "상품 선택" and len(rates_df):
            comp = st.selectbox("보험사", sorted(rates_df["회사명"].dropna().unique()))
            sub = rates_df[rates_df["회사명"] == comp]
            prod_label = st.selectbox("상품명", sorted(sub["상품명"].dropna().unique()))
            sub = sub[sub["상품명"] == prod_label]
            kind = st.selectbox("종 구분", sorted(sub["종구분"].dropna().astype(str).unique()))
            sub = sub[sub["종구분"].astype(str) == kind]
            term = st.selectbox("납입기간", sorted(sub["납입기간"].dropna().astype(str).unique()))
            row = sub[sub["납입기간"].astype(str) == term].iloc[0]
            rate_cols = [c for c in rates_df.columns if c.endswith("차월")]
            series = [float(row[c]) if pd.notna(row[c]) else 0.0 for c in rate_cols[:36]]
            series += [series[-1]] * (36 - len(series))
            rates = [r / 100 if r > 1.5 else r for r in series]
            st.caption(f"출처: {row['파일']}")
        else:
            if mode == "상품 선택":
                st.warning("환급률표가 없습니다. 위에서 업로드하거나 직접 입력을 사용하세요.")
            c1, c2, c3 = st.columns(3)
            r12 = c1.number_input("12차월 %", 0, 100, 30) / 100
            r24 = c2.number_input("24차월 %", 0, 100, 48) / 100
            r36 = c3.number_input("36차월 %", 0, 100, 60) / 100
            rates = [refund_rate(m, r12, r24, r36) for m in range(1, 37)]

        pc1, pc2 = st.columns(2)
        if pc1.button("사례 A · 90만", use_container_width=True):
            st.session_state["preset_fee"] = 90.0
            st.rerun()
        if pc2.button("사례 B · 70만", use_container_width=True):
            st.session_state["preset_fee"] = 70.0
            st.rerun()
        st.caption("금융위 가이드 원문 사례 (월납 10만 기준)")

if "preset_fee" in st.session_state:
    fee = st.session_state.pop("preset_fee")

# ──────────────── 계산 ────────────────
elapsed = max(1, (date.today().year - start.year) * 12 + (date.today().month - start.month) + 1)
m_now = min(elapsed, 36)
df = arbitrage_table(P, fee, rates)
risk_months = df[df["위험"]]["차월"].tolist()
idx = round(len(risk_months) / 36 * 100)
now = df[df["차월"] == m_now].iloc[0]
paid_now, cv_now, agent_now = now["납입누계"], now["예상환급금"], now["설계사측수취"]
clawback = max(0.0, agent_now - paid_now)
refund12 = df[df["차월"] == 12].iloc[0]["예상환급금"]
remain1200 = max(0.0, P * 12 - fee - refund12)

with right:
    # ──────── 판정 (마스코트) ────────
    if elapsed > 36:
        ui.speak("safe", f"경과 {elapsed}차월 — 차익거래 점검기간(36차월)이 지난 계약입니다.",
                 "아래 표는 참고용 36차월 기준입니다.", tone="bb-safe", big="🟢 점검기간 종료")
    elif clawback > 0:
        ui.speak("warn", f"지금({m_now}차월) 해지되면 약 <b>{clawback:,.1f}만원</b>이 환수돼요!",
                 f"수수료 {fee:,.0f}만 + 환급금 {cv_now:,.1f}만 = {agent_now:,.1f}만 > 납입 {paid_now:,.0f}만. "
                 f"위험 구간: {risk_months[0]}~{risk_months[-1]}차월 (지수 {idx}/100)",
                 tone="bb-warn", big="🔴 환수 위험!")
    elif risk_months:
        ui.speak("think", f"지금({m_now}차월)은 안전하지만, <b>{risk_months[0]}~{risk_months[-1]}차월</b>이 위험 구간이에요.",
                 f"그 구간에서 해지·실효되면 초과분이 환수됩니다. (지수 {idx}/100)",
                 tone="bb-amber", big="🟡 구간 주의")
    else:
        ui.speak("safe", "36개월 전 구간에서 차익거래가 발생하지 않아요.",
                 "실제 판정은 해지 시점 환급금 기준입니다.", tone="bb-safe", big="🟢 안전합니다!")

    # ──────── ② 계약사항 + ③ 요약 ────────
    i1, i2 = st.columns([1.15, 1], gap="medium")
    with i1:
        st.markdown(
            f"""<div style="border:1.5px solid #E6ECF7;border-radius:14px;padding:14px 18px;font-size:.95rem">
            <b>② 계약사항</b><br>
            <table style="width:100%;margin-top:6px;border-collapse:collapse">
            <tr><td style="color:#6E7A94;padding:3px 0;width:32%">상품명</td><td>{prod_label if mode=='상품 선택' else '직접 입력'}</td></tr>
            <tr><td style="color:#6E7A94;padding:3px 0">보험사 / 종구분</td><td>{comp} / {kind}</td></tr>
            <tr><td style="color:#6E7A94;padding:3px 0">계약일자</td><td>{start.strftime('%Y-%m-%d')}{' · ' + policy_no if policy_no else ''}</td></tr>
            <tr><td style="color:#6E7A94;padding:3px 0">경과차월</td><td><b style="color:#3D6BFF">{elapsed}차월</b> (자동)</td></tr>
            <tr><td style="color:#6E7A94;padding:3px 0">기납입보험료</td><td>{paid_now:,.0f}만원 (자동)</td></tr>
            </table></div>""", unsafe_allow_html=True)
    with i2:
        ui.stat("pc-sky", f"{cv_now / paid_now * 100 if paid_now else 0:,.1f}%",
                "③ 현재 예상 환급률", f"{m_now}차월 기준")
        st.write("")
        if agent_now > paid_now:
            ui.stat("pc-peach", f"{agent_now:,.1f}만", "수수료+환급금 합계", f"납입 {paid_now:,.0f}만 초과 ⚠")
        else:
            ui.stat("pc-mint", f"{agent_now:,.1f}만", "수수료+환급금 합계", f"납입 {paid_now:,.0f}만 이내 ✓")

    st.write("")
    # ──────── ④ 차월별 환급 예시 + ⑤ 규제 진단 ────────
    t1, t2 = st.columns([1.3, 1], gap="medium")
    with t1:
        st.markdown("**④ 차월별 환급·판정 예시**")
        marks = sorted(set([6, 12, 18, 24, 30, 36] + [m_now]))
        show = df[df["차월"].isin(marks)].copy()
        show["환급률"] = (show["예상환급금"] / show["납입누계"] * 100).round(1)
        show["판정"] = show["위험"].map({True: "⚠️ 위험", False: "✅ 안전"})
        show["차월"] = show["차월"].astype(str) + "차월"
        show.loc[show["차월"] == f"{m_now}차월", "차월"] = f"▶ {m_now}차월 (현재)"
        st.dataframe(
            show[["차월", "납입누계", "예상환급금", "환급률", "판정"]]
            .style.format({"납입누계": "{:,.0f}만", "예상환급금": "{:,.1f}만", "환급률": "{:.1f}%"}),
            use_container_width=True, hide_index=True)
    with t2:
        st.markdown("**⑤ 규제 진단**")
        ui.p_card("pc-peach" if risk_months else "pc-mint", "차익거래",
                  f"{risk_months[0]}~{risk_months[-1]}차월 위험" if risk_months else "전 구간 안전",
                  f"위험지수 {idx}/100. 위험 구간 해지·실효 시 초과분 환수." if risk_months
                  else "이 조건에서는 환수가 발생하지 않습니다.")
        st.write("")
        ui.p_card("pc-lavender", "1,200% 잔여한도", f"약 {remain1200:,.1f}만원",
                  f"연납보험료 {P * 12:,.0f}만 − 수수료 {fee:,.0f}만 − 1년시점 예상환급금 {refund12:,.1f}만. "
                  "<b>공통비 배분액 미반영</b> 참고치입니다.")

    # ──────── 차트 ────────
    plot = df.melt(id_vars=["차월", "위험"], value_vars=["납입누계", "설계사측수취"],
                   var_name="구분", value_name="금액")
    plot["구분"] = plot["구분"].map({"납입누계": "고객이 낸 보험료",
                                     "설계사측수취": "수수료 + 해약환급금"})
    base = alt.Chart(plot).encode(x=alt.X("차월:Q", title="경과 차월",
                                          scale=alt.Scale(domain=[1, 36]),
                                          axis=alt.Axis(gridColor="#EDF1FA")))
    lines = base.mark_line(strokeWidth=3).encode(
        y=alt.Y("금액:Q", title="금액 (만원)", axis=alt.Axis(gridColor="#EDF1FA")),
        color=alt.Color("구분:N", title=None,
                        scale=alt.Scale(domain=["고객이 낸 보험료", "수수료 + 해약환급금"],
                                        range=["#9AA5B8", "#3D6BFF"]),
                        legend=alt.Legend(orient="bottom", labelFontSize=13.5, labelFontWeight=700)),
        strokeDash=alt.condition(alt.datum.구분 == "고객이 낸 보험료",
                                 alt.value([6, 4]), alt.value([0])),
        tooltip=["차월", "구분", alt.Tooltip("금액:Q", format=",.1f")],
    )
    shade = (alt.Chart(df[df["위험"]]).mark_rect(color="#FF5D5D", opacity=0.14)
             .encode(x=alt.X("차월:Q"), x2=alt.X2("차월2:Q"))
             .transform_calculate(차월2="datum.차월 + 1"))
    now_rule = (alt.Chart(pd.DataFrame({"차월": [m_now]}))
                .mark_rule(color="#2BC48A", strokeWidth=2, strokeDash=[3, 3])
                .encode(x="차월:Q"))
    st.altair_chart((shade + lines + now_rule).properties(height=280, background="#FFFFFF"),
                    use_container_width=True)
    st.caption("붉은 음영 = 위험 구간 · 초록 점선 = 현재 경과차월. 실효(미납)는 최초 미납 시점 기준, 사망 소멸은 제외.")

    @st.dialog("〔연별환급예시〕 36개월 상세 판정", width="large")
    def show_table():
        full = df.copy()
        full["환급률"] = (full["예상환급금"] / full["납입누계"] * 100).round(1)
        full["판정"] = full["위험"].map({True: "⚠️ 환수 위험", False: "✅ 안전"})
        st.dataframe(
            full[["차월", "납입누계", "예상환급금", "환급률", "설계사측수취", "판정"]]
            .style.format({"납입누계": "{:,.0f}만", "예상환급금": "{:,.1f}만",
                           "환급률": "{:.1f}%", "설계사측수취": "{:,.1f}만"}),
            use_container_width=True, hide_index=True, height=520)
        st.caption("판정 산식: 수수료등 + 해약환급금 − 환수금 > 납입보험료 (개정 FAQ Q11 · 제5차 TF 확정)")

    b1, _ = st.columns([1.3, 1.7])
    if b1.button("📄 연별환급예시 (36개월 전체)", type="primary", use_container_width=True):
        show_table()

st.caption("⑥ 본 화면은 보험사 제공 예상 해약환급률표 기준의 예시 산출로 실제 환급금과 다를 수 있으며, "
           "차익거래·1,200% 판정은 보험사 정산 기준이 우선합니다. 고객 안내·교부용이 아닌 내부 참고용입니다.")
