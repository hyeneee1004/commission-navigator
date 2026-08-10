# -*- coding: utf-8 -*-
r"""데이터 스토어 — 폴더에 파일을 넣으면 자동 반영 (NotebookLM 방식).

data\참고자료\   : PDF·PPTX·XLSX·TXT → [규정 찾기] 문서 검색에 자동 포함
data\수수료규정\ : 생보 수수료 규정 xlsx(사업가형 양식) → [소득 계산] 실제 수수료율
data\환급률표\   : 보험사 해약환급률표 → [환수 체크] 상품 선택

캐시는 (파일명, 수정시각, 크기) 서명 기준 → 파일을 추가·교체하면 새로고침 시 즉시 반영.
"""
import re
from pathlib import Path

import pandas as pd
import streamlit as st

IS_PUBLIC = (Path(__file__).parent / "PUBLIC.flag").exists()
DATA_DIR = Path(__file__).parent / "data"
DOC_DIR = DATA_DIR / "참고자료"
REG_DIR = DATA_DIR / "수수료규정"
REFUND_DIR = DATA_DIR / "환급률표"

for _d in (DOC_DIR, REG_DIR, REFUND_DIR):
    _d.mkdir(parents=True, exist_ok=True)

DOC_EXTS = {".pdf", ".pptx", ".xlsx", ".xlsm", ".txt", ".md"}


def _sig(folder: Path, exts) -> tuple:
    """폴더 상태 서명 — 파일 추가/변경 시 캐시 자동 무효화."""
    out = []
    if folder.is_dir():
        for f in sorted(folder.iterdir()):
            if f.suffix.lower() in exts and not f.name.startswith("~$"):
                s = f.stat()
                out.append((f.name, int(s.st_mtime), s.st_size))
    return tuple(out)


# ──────────────────────── 참고자료 텍스트 추출 ────────────────────────
@st.cache_data(show_spinner=False)
def _extract_file(path_str: str, _mtime: int) -> list:
    """파일 → [(위치, 텍스트)] 청크. 실패 시 빈 목록."""
    p = Path(path_str)
    chunks = []
    try:
        ext = p.suffix.lower()
        if ext == ".pdf":
            import pdfplumber
            with pdfplumber.open(p) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    t = (page.extract_text() or "").strip()
                    if t:
                        chunks.append((f"{i}쪽", t))
        elif ext == ".pptx":
            from pptx import Presentation
            for i, slide in enumerate(Presentation(str(p)).slides, 1):
                parts = []
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        parts.append(shape.text_frame.text)
                    if getattr(shape, "has_table", False):
                        for row in shape.table.rows:
                            parts.append(" | ".join(c.text for c in row.cells))
                t = "\n".join(x for x in parts if x.strip())
                if t:
                    chunks.append((f"슬라이드 {i}", t))
        elif ext in (".xlsx", ".xlsm"):
            import openpyxl
            wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
            for name in wb.sheetnames[:20]:
                ws = wb[name]
                lines = []
                for row in ws.iter_rows(max_row=500, values_only=True):
                    line = " ".join(str(c) for c in row if c is not None and str(c).strip())
                    if line:
                        lines.append(line)
                if lines:
                    chunks.append((f"시트 {name}", "\n".join(lines)))
            wb.close()
        else:  # txt, md
            chunks.append(("본문", p.read_text(encoding="utf-8", errors="ignore")))
    except Exception:
        pass
    return chunks


def doc_index() -> list:
    """[(파일명, 위치, 텍스트)] 전체 색인."""
    rows = []
    for name, mtime, _size in _sig(DOC_DIR, DOC_EXTS):
        for loc, text in _extract_file(str(DOC_DIR / name), mtime):
            rows.append((name, loc, text))
    return rows


def doc_files() -> list:
    """로딩된 참고자료 요약: [(파일명, 청크수)]."""
    counts = {}
    for name, _loc, _t in doc_index():
        counts[name] = counts.get(name, 0) + 1
    return sorted(counts.items())


def search_docs(query: str, limit: int = 12, ctx: int = 90) -> list:
    """키워드 검색 → [{file, loc, snippet}] (일치 부분 **강조**)."""
    q = query.strip()
    if len(q) < 2:
        return []
    out, seen = [], set()
    pat = re.compile(re.escape(q), re.IGNORECASE)
    for name, loc, text in doc_index():
        for m in pat.finditer(text):
            s, e = max(0, m.start() - ctx), min(len(text), m.end() + ctx)
            snippet = re.sub(r"\s+", " ", text[s:e]).strip()
            snippet = pat.sub(lambda x: f"**:red[{x.group(0)}]**", snippet)
            key = (name, loc)
            if key in seen:
                continue
            seen.add(key)
            out.append({"file": name, "loc": loc, "snippet": snippet})
            break  # 파일·위치당 첫 일치만
        if len(out) >= limit:
            break
    return out


# ──────────────────────── 수수료 규정(실제 수수료율) ────────────────────────
@st.cache_data(show_spinner="수수료 규정 읽는 중…")
def _parse_regulation(path_str: str, _mtime: int) -> pd.DataFrame:
    """사업가형 규정 양식 파싱 → [구간, 보험사, 상품군, 초회, 1차년, 총계, 1차년비중]."""
    import openpyxl
    p = Path(path_str)
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    rows = []
    for sheet in wb.sheetnames:
        if "규정" in sheet or "표지" in sheet or "개정" in sheet:
            continue
        ws = wb[sheet]
        grid = [list(r) for r in ws.iter_rows(max_row=400, max_col=80, values_only=True)]
        if len(grid) < 5:
            continue
        # 헤더 행 전부 탐색: '상품군'이 있고 다음 행에 회차 헤더('초회'/'계')가 있는 행만
        hdrs = [i for i, r in enumerate(grid[:-1])
                if any(str(c).strip() == "상품군" for c in r if c)
                and any(str(c).split("\n")[0].strip() in ("초회", "계") for c in grid[i + 1] if c)]
        for hi, hdr in enumerate(hdrs):
            if hdr + 2 >= len(grid):
                continue
            end = hdrs[hi + 1] if hi + 1 < len(hdrs) else len(grid)
            name_row, sub_row = grid[hdr], grid[hdr + 1]
            prod_col = next(j for j, c in enumerate(name_row) if c and str(c).strip() == "상품군")
            # 보험사 블록: 헤더 행에서 상품군 오른쪽의 비어있지 않은 셀
            blocks = [(j, re.split(r"[(\n]", str(c))[0].strip())
                      for j, c in enumerate(name_row[prod_col + 1:], prod_col + 1) if c and str(c).strip()]
            for bi, (j0, insurer) in enumerate(blocks):
                j1 = blocks[bi + 1][0] if bi + 1 < len(blocks) else len(sub_row)
                subs = {str(sub_row[j]).split("\n")[0].strip(): j
                        for j in range(j0, min(j1, len(sub_row))) if sub_row[j]}
                c_first = subs.get("초회")
                c_y1 = subs.get("1차년")
                c_tot = subs.get("계")
                if c_tot is None:
                    continue
                seg = ""  # '구분' 열(실적구간) — 병합 셀이므로 값을 이어받음
                for r in grid[hdr + 2:end]:
                    if prod_col >= 1 and prod_col - 1 < len(r) and r[prod_col - 1] \
                            and str(r[prod_col - 1]).strip():
                        seg = str(r[prod_col - 1]).strip().replace("\n", "")
                    prod = r[prod_col] if prod_col < len(r) else None
                    if not prod or not str(prod).strip():
                        continue

                    def num(idx):
                        try:
                            return float(r[idx]) if idx is not None and r[idx] is not None else 0.0
                        except (TypeError, ValueError):
                            return 0.0
                    first, y1, tot = num(c_first), num(c_y1), num(c_tot)
                    if tot <= 0:
                        continue
                    rows.append(dict(구간=sheet.strip(), 세부구간=seg, 보험사=insurer,
                                     상품군=str(prod).strip(),
                                     초회=first, 첫해지급=first + y1, 총계=tot,
                                     첫해비중=round((first + y1) / tot * 100, 1)))
    wb.close()
    return pd.DataFrame(rows)


def load_regulations() -> tuple:
    """수수료규정 폴더의 최신 파일 파싱. 반환: (파일명 or None, DataFrame)."""
    sig = _sig(REG_DIR, {".xlsx", ".xlsm"})
    if not sig:
        return None, pd.DataFrame()
    # 최신 수정 파일 사용
    name, mtime, _ = max(sig, key=lambda x: x[1])
    df = _parse_regulation(str(REG_DIR / name), mtime)
    return name, df


def clear_caches():
    _extract_file.clear()
    _parse_regulation.clear()


def save_uploads(folder: Path, uploaded_files) -> int:
    """업로드 파일을 폴더에 영구 저장. 동일 이름·크기 파일은 건너뜀. 반환: 새로 저장한 수."""
    if IS_PUBLIC:
        return 0
    saved = 0
    for uf in uploaded_files or []:
        dest = folder / uf.name
        data = uf.getbuffer()
        if dest.exists() and dest.stat().st_size == len(data):
            continue
        dest.write_bytes(data)
        saved += 1
    if saved:
        clear_caches()
    return saved


def uploader_block(st_mod, folder: Path, label: str, types, key: str):
    """공용 업로드 UI: 저장 → 즉시 반영. (st_mod = streamlit 모듈)"""
    if IS_PUBLIC:
        st_mod.caption("공개판에서는 파일 업로드가 지원되지 않습니다. 회사 규정·환급률표 연동은 내부판에서 이용하세요.")
        return
    files = st_mod.file_uploader(label, type=types, accept_multiple_files=True, key=key)
    n = save_uploads(folder, files)
    if n:
        st_mod.success(f"{n}개 파일을 저장했습니다. 바로 반영됩니다.", icon="✅")
    existing = [f.name for f in sorted(folder.iterdir())
                if f.is_file() and not f.name.lower().endswith(".txt")]
    if existing:
        st_mod.caption("보관 중: " + " · ".join(existing))
