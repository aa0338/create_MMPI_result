import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import matplotlib.font_manager as fm

warnings.filterwarnings("ignore")

st.set_page_config(page_title="MMPI-2 프로파일 그래프", layout="wide")

font_candidates = ["NanumGothic", "Nanum Gothic", "DejaVu Sans"]

available_fonts = {f.name for f in fm.fontManager.ttflist}

for font_name in font_candidates:
    if font_name in available_fonts:
        plt.rc("font", family=font_name)
        break

plt.rcParams["axes.unicode_minus"] = False


def create_base_data():
    x1 = ["VRIN", "TRIN", "trin(T/F)", "F", "F(B)", "F(P)", "FBS", "L", "K", "S"]
    x2 = ["Hs", "D", "Hy", "Pd", "Mf", "Pa", "Pt", "Sc", "Ma", "Si"]

    y1 = [61, 61, "T", 58, 55, 52, 53, 40, 50, 62]
    y2 = [61, 58, 59, 48, 49, 55, 56, 61, 62, 65]

    x = x1 + [""] + x2
    y = y1 + [""] + y2

    return pd.DataFrame({
        "x": x,
        "y": [str(v) if v != "" else "" for v in y]
    })


st.title("MMPI-2 프로파일 그래프 생성기")
st.write("표에서 y값을 직접 수정하세요. 문자값이 들어간 행은 그래프 출력 전에 자동으로 제외됩니다.")

base_data = create_base_data()

edited_data = st.data_editor(
    base_data,
    hide_index=True,
    num_rows="fixed",
    disabled=["x"],
    column_config={
        "x": st.column_config.TextColumn("척도", width="medium"),
        "y": st.column_config.TextColumn("점수", width="small")
    },
    use_container_width=True
)

work_data = edited_data.copy()

# 공백 정리
work_data["y"] = work_data["y"].astype("string").str.strip()
work_data.loc[work_data["y"] == "", "y"] = pd.NA

# 숫자로 변환 가능한 값만 숫자로 저장
work_data["y_num"] = pd.to_numeric(work_data["y"], errors="coerce")

# trin(T/F)의 T/F 값 저장
trin_tf_value = ""

trin_tf_rows = work_data.loc[work_data["x"] == "trin(T/F)", "y"]

if not trin_tf_rows.empty and pd.notna(trin_tf_rows.iloc[0]):
    trin_tf_value = str(trin_tf_rows.iloc[0])

# 규칙
# 1. 숫자인 행은 유지
# 2. 빈칸 행은 유지 (가운데 끊김용)
# 3. 숫자로 변환 안 되는 문자행은 제거
plot_data = work_data[work_data["y"].isna() | work_data["y_num"].notna()].copy().reset_index(drop=True)

left_col, right_col = st.columns([3, 2])

with right_col:
    st.subheader("현재 입력값")
    st.dataframe(edited_data, hide_index=True, use_container_width=True)

with left_col:
    st.subheader("그래프")

    if plot_data["y_num"].notna().sum() == 0:
        st.warning("그래프에 표시할 숫자 데이터가 없습니다.")
    else:
        x_pos = np.arange(len(plot_data))
        x_labels = plot_data["x"].fillna("").tolist()

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(
            x_pos,
            plot_data["y_num"],
            color="blue",
            linewidth=2
        )

        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels)

        ax.set_ylim(20, 120)
        ax.set_yticks(np.arange(20, 121, 10))
        # ax.set_title("MMPI_profile_input MMPI-2 검사결과")
        ax.grid(True, axis="y", alpha=0.3)
        ax.axhline(y=65, linewidth=0.2, color="black")
        
        separator_idx = plot_data.index[plot_data["x"].eq("")][0]

        ax.axvline(
            x=separator_idx,
            color="black",
            linewidth=0.3,
            linestyle="--"
        )

        # 기준선
        ax.axhline(65, color="black", linewidth=0.6)

        # 점수 표시
        for i, row in plot_data.iterrows():
            if pd.isna(row["y_num"]):
                continue

            y_value = row["y_num"]

            if float(y_value).is_integer():
                label = str(int(y_value))
            else:
                label = str(y_value)

            # TRIN에는 trin(T/F) 값을 뒤에 붙임
            if row["x"] == "TRIN" and trin_tf_value != "":
                label = label + trin_tf_value

            ax.text(
                i,
                y_value + 2,
                label,
                color="blue",
                ha="center",
                va="bottom",
                fontsize=10
            )

        st.pyplot(fig, use_container_width=True)