# -*- coding: utf-8 -*-
"""소득 계산 — 실제 규정 기반 개편 전후 소득 비교 (계약 진단과 동일한 ①입력/②결과 구성)."""
import altair as alt
import pandas as pd
import streamlit as st

import doc_store
import ui
from portal_data import simulate

st.set_page_config(page_title="소득 계산 — 수수료 내비게이터", page_icon="🧭", layout="wide",
                   initial_sidebar_state="collapsed")
ui.inject()
ui.tabbar("sim")
ui.page_head("💰 내 소득, 얼마나 달라지나",
             "실제 수수료 규정 기준으로 '27년(4년 분급)·'29년(7년 분급) 첫해 소득과 필요 실적을 계산합니다.<br>"
             "계약체결비용·선지급률은 <b>3차 FAQ 확정 전 잠정치</b>예요.",
             mood="think", say="숫자만 넣으면 제가 바로 계산해 드릴게요!")

st.write("")
left, right = st.columns([1, 2], gap="large")

# ──────────────── ① 조건 입력 ────────────────
with left:
    with st.container(border=True):
        st.markdown("**① 조건 입력**")
        c1, c2 = st.columns(2)
        P = c1.number_input("월 보험료 (만원)", 1.0, 1000.0, 10.0, 1.0)
        N = c2.number_input("월 신계약 건수", 0.5, 100.0, 3.0, 0.5)

        reg_file, reg_df = doc_store.load_regulations()
        mode = st.radio("수수료율 기준", ["📂 실제 규정", "직접 입력"], horizontal=True,
                        index=0 if len(reg_df) else 1)

        T0, R1 = 1300.0, 85.0
        sel_key = "manual"
        first_pay = None
        if mode == "📂 실제 규정" and len(reg_df):
            segs = list(dict.fromkeys(reg_df["세부구간"]))
            seg = st.selectbox("실적구간(등급)", segs)
            sub = reg_df[reg_df["세부구간"] == seg]
            comp = st.selectbox("보험사", sorted(sub["보험사"].unique()))
            sub = sub[sub["보험사"] == comp]
            prod = st.selectbox("상품군", list(sub["상품군"]))
            row = sub[sub["상품군"] == prod].iloc[0]
            conv = st.number_input("환산율 (%)", 10, 300, 100, 5,
                                   help="규정 지급률은 '환산월초' 기준. 회사별 환산율을 입력하세요. "
                                        "100% 초과 환산(예: 120%)도 입력 가능합니다.") / 100
            T0 = float(row["총계"]) * conv
            R1 = float(row["첫해비중"])
            first_pay = float(row["첫해지급"]) * conv
            sel_key = f"{seg}|{comp}|{prod}|{conv}"
            st.caption(f"📂 {reg_file}\n\n{comp} · {prod} · {seg} : "
                       f"월P 대비 총 **{T0:,.1f}%**, 첫해 {first_pay:,.1f}% ({R1:.1f}%)")
            if any(k in prod for k in ("연금", "저축", "VUL", "변액")):
                st.warning("연금·저축·변액은 환산율이 100%가 아닌 경우가 많아요. 환산율을 확인하세요.", icon="⚠️")
        elif mode == "📂 실제 규정":
            st.warning("규정 파일이 없습니다. 아래에 업로드하거나 직접 입력을 사용하세요.")
            mode = "직접 입력"

        with st.expander("⚙️ 세부 조건 (시상·계약체결비용·선지급)"):
            if mode == "직접 입력":
                T0 = float(st.number_input("현행 총 수수료율 (%)", 100, 3000, 1300, 50))
                R1 = float(st.number_input("1차년 지급 비중 (%)", 10, 100, 85, 5))
                c_def, s_def = 1200.0, 700.0
            else:
                st.caption(f"총 수수료율 {T0:,.1f}% · 1차년 비중 {R1:.1f}% (규정값)")
                c_def, s_def = round(T0), round(min(first_pay, T0))
            BONUS = st.number_input("시상금 비율 (%)", 0, 1000, 200, 50)
            C_pct = st.number_input("계약체결비용 (%)", 100.0, 3000.0, float(c_def), 50.0,
                                    key=f"C_{sel_key}",
                                    help="개편 후 한도 기준. 규정 선택 시 '현행 총 수수료율과 동일' 가정")
            S_pct = st.number_input("선지급률 (%)", 0.0, 2000.0, float(s_def), 50.0,
                                    key=f"S_{sel_key}",
                                    help="규정 선택 시 '현행 첫해 지급률과 동일' 가정")

        with st.expander("📤 수수료 규정 파일 업로드·관리"):
            doc_store.uploader_block(st, doc_store.REG_DIR,
                                     "새 규정 xlsx(사업가형 양식)를 올리면 최신 파일 기준으로 바로 반영됩니다",
                                     ["xlsx", "xlsm"], "up_reg")

# ──────────────── 계산 ────────────────
res = simulate(P, T0, R1, BONUS, C_pct, S_pct)
cur1 = res["현행"][0]
y4 = res["'27.1 (4년 분급)"][0]
y7 = res["'29.1 (7년 분급)"][0]
k4, k7 = cur1 / y4, cur1 / y7
drop4 = (1 - y4 / cur1) * 100

# ──────────────── ② 결과 요약 ────────────────
with right:
    st.markdown("**② 결과 요약**")
    h1, h2, h3 = st.columns(3, gap="medium")
    with h1:
        ui.stat("pc-sky", f"{cur1 * N:,.0f}만원", "지금 첫해 월 소득", f"월 {N:g}건 기준")
    with h2:
        if drop4 >= 0:
            ui.stat("pc-peach", f"−{drop4:.0f}%", "'27년, 같은 실적이면",
                    f"첫해 월 {y4 * N:,.0f}만원으로 감소")
        else:
            ui.stat("pc-mint", f"+{-drop4:.0f}%", "'27년, 같은 실적이면",
                    f"첫해 월 {y4 * N:,.0f}만원으로 증가")
    with h3:
        ui.stat("pc-lemon", f"×{k4:.1f}~{k7:.1f}", "지금 소득 지키려면",
                f"월 {N * k4:.1f}건('27) → {N * k7:.1f}건('29)")

    st.write("")
    if drop4 >= 25:
        ui.speak("warn", f"같은 실적이면 '27년 첫해 소득이 <b>{drop4:.0f}%</b> 줄어요! "
                 f"지금 소득을 지키려면 월 <b>{N * k4:.1f}건</b>이 필요해요.",
                 "하지만 분할 수수료가 쌓이면 1년 반~2년 뒤부터는 회복됩니다.", tone="bb-warn")
    elif drop4 >= 0:
        ui.speak("safe", "감소폭이 크지 않아요. 유지율만 관리하면 충분히 방어할 수 있습니다.", tone="bb-safe")
    else:
        ui.speak("happy", "이 조건에서는 개편 후 첫해 수령액이 오히려 늘어나요. "
                 "계약체결비용·선지급률 가정을 다시 확인해 보세요.", tone="bb-safe")

    # ── ③ 시나리오 비교 ──
    st.markdown("**③ 시나리오 비교** (첫해 수령액, 계약 1건)")
    df = pd.DataFrame([(k, v[0]) for k, v in res.items()], columns=["구분", "첫해 수령액"])
    chart = (
        alt.Chart(df)
        .mark_bar(height=30, cornerRadiusEnd=6)
        .encode(
            x=alt.X("첫해 수령액:Q", title=None, axis=alt.Axis(gridColor="#E8EDF4")),
            y=alt.Y("구분:N", sort=None, title=None,
                    axis=alt.Axis(labelFontSize=13.5, labelFontWeight=700, labelColor="#152238")),
            color=alt.condition(alt.datum.구분 == "현행", alt.value("#2456A6"), alt.value("#A9C4EE")),
            tooltip=["구분", alt.Tooltip("첫해 수령액:Q", format=",.1f")],
        ).properties(height=200)
    )
    text = chart.mark_text(align="left", dx=6, fontSize=14, fontWeight=800, color="#152238").encode(
        text=alt.Text("첫해 수령액:Q", format=",.0f"))
    st.altair_chart((chart + text).properties(background="#FFFFFF"), use_container_width=True)

    @st.dialog("상세 계산표·산식", width="large")
    def show_detail():
        dd = pd.DataFrame(
            [(k, v[0], v[0] / cur1 * 100, v[1]) for k, v in res.items()],
            columns=["구분", "1차년 수령액/건", "현행 대비(%)", "총수령액/건(완납유지)"])
        st.dataframe(dd.style.format({"1차년 수령액/건": "{:,.1f}만원", "현행 대비(%)": "{:.0f}%",
                                      "총수령액/건(완납유지)": "{:,.1f}만원"}),
                     use_container_width=True, hide_index=True)
        st.code(
            """현행 1차년      = P × 총수수료율 × 1차년비중 + P × 시상률
'26.7 (1,200%)  = MIN(현행 1차년, P × 12)          ← 보장성, 증권번호 단위
계약체결비용 C   = P × 계약체결비용률
선지급 S        = MIN(P × 선지급률, C)             ← 선지급 ≤ 계약체결비용 100%
4년 분급 월액    = MIN(C × 1.5%, C × 90% / 48)
7년 분급 월액    = MIN(C × 0.8%, C × 100% / 84) , 장기유지(61~84차월) = C × 0.4%""",
            language="text")
        st.caption("계약체결비용·선지급률은 보험사·상품별 값. 3차 FAQ('26.8월~) 확정 전 잠정치입니다.")

    b1, _ = st.columns([1.3, 1.7])
    if b1.button("📄 상세 계산표·산식 보기", use_container_width=True):
        show_detail()

# ──────────────── ④ 대응 가이드 (결과 맞춤) ────────────────
st.write("")
st.markdown("### ④ 나는 어떻게 대응하면 될까")
tot7, totc = res["'29.1 (7년 분급)"][1], res["현행"][1]

# 손익분기 차월: 계약 1건 기준, 분급 누적 수령액이 현행 첫해 수령액을 따라잡는 시점
C_amt = P * C_pct / 100.0
S_amt = min(P * S_pct / 100.0, C_amt)
m4_amt = min(C_amt * 0.015, C_amt * 0.90 / 48)
t4 = (cur1 - S_amt) / m4_amt if m4_amt > 0 else 999
if t4 <= 0:
    be_txt = "이 조건에서는 선지급만으로 이미 현행 첫해 수령액 이상이에요."
elif t4 <= 48:
    be_txt = f"계약 1건 기준, 분급 누적 수령액이 현행 첫해 수령액을 <b>약 {t4:.0f}차월</b>에 따라잡아요."
else:
    be_txt = "이 가정에서는 4년(48개월) 분급만으로 현행 첫해 수령액을 다 못 따라잡아요. 유지와 증건을 병행해야 해요."

reco_keep = drop4 >= 30          # 감소폭 크면 '소득 유지형', 아니면 '장기 축적형' 추천
cards = [
    dict(theme="pc-sky", tag="소득 유지형",
         head=f"평소 실적의 {k4:.1f}~{k7:.1f}배를 목표로",
         body=f"지금 월 {N:g}건 → '27년 <b>월 {N * k4:.1f}건 (+{N * (k4 - 1):.1f}건)</b>, "
              f"'29년 월 {N * k7:.1f}건. 당장 이번 달 소득을 지키는 가장 직접적인 방법이에요.",
         badge=reco_keep),
    dict(theme="pc-mint", tag="장기 축적형",
         head="무리한 증건보다 오래 유지",
         body=(f"완납 유지 시 계약 1건당 <b>{totc:,.0f}만원 → {tot7:,.0f}만원</b>. " if tot7 > totc else "")
              + be_txt + " 핵심은 <b>'더 오래 유지되는 계약'</b>이에요.",
         badge=not reco_keep),
    dict(theme="pc-lavender", tag="신인 특례 참고",
         head="직전 3년 무경력이면 지원비 별도",
         body="신인활동지원비(등록 1년 내)는 1,200%·차익거래 계산에서 <b>제외</b>되고 환수 대상도 아니에요. "
              "모집경력조회시스템으로 사전 확인 필수. 단, 13차월 이후 지급분은 포함.",
         badge=False),
]
cards.sort(key=lambda c: not c["badge"])     # 추천 카드를 맨 앞으로
gcols = st.columns(3, gap="medium")
for col, cd in zip(gcols, cards):
    with col:
        ui.p_card(cd["theme"], cd["tag"], cd["head"], cd["body"], badge=cd["badge"])
