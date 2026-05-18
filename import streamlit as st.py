import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="태풍 이동 경로 시각화",
    layout="wide"
)

st.title("🌀 태풍 이동 경로 데이터 시각화 사이트")

# -----------------------------
# 데이터 불러오기
# -----------------------------
df = pd.read_csv("data/typhoon_sample.csv")

df["datetime"] = pd.to_datetime(df["datetime"])

# -----------------------------
# 사이드바 옵션
# -----------------------------
st.sidebar.header("태풍 설정")

typhoon_list = df["typhoon"].unique()

selected_typhoon = st.sidebar.selectbox(
    "태풍 선택",
    typhoon_list
)

speed = st.sidebar.slider(
    "재생 속도 (배속)",
    0.1,
    3.0,
    1.0,
    0.1
)

# 태풍 필터
filtered_df = df[df["typhoon"] == selected_typhoon]

# -----------------------------
# 지도 영역
# -----------------------------
map_placeholder = st.empty()

# -----------------------------
# 재생 버튼
# -----------------------------
start_button = st.button("▶ 태풍 이동 시작")

# -----------------------------
# 애니메이션 실행
# -----------------------------
if start_button:

    path_lats = []
    path_lons = []

    for i in range(len(filtered_df)):

        current = filtered_df.iloc[i]

        path_lats.append(current["lat"])
        path_lons.append(current["lon"])

        fig = go.Figure()

        # 태풍 이동 경로
        fig.add_trace(
            go.Scattergeo(
                lon=path_lons,
                lat=path_lats,
                mode='lines+markers',
                line=dict(width=4, color='red'),
                marker=dict(size=10, color='blue'),
                name='태풍 경로'
            )
        )

        # 현재 태풍 위치
        fig.add_trace(
            go.Scattergeo(
                lon=[current["lon"]],
                lat=[current["lat"]],
                mode='markers',
                marker=dict(size=18, color='red'),
                name='현재 위치'
            )
        )

        # 지도 설정
        fig.update_geos(
            projection_type="mercator",
            showcountries=True,
            showcoastlines=True,
            lataxis_range=[30, 40],
            lonaxis_range=[124, 132],
            resolution=50
        )

        fig.update_layout(
            height=700,
            margin={"r":0,"t":0,"l":0,"b":0},
            title=f"""
            태풍: {selected_typhoon}
            <br>
            시간: {current['datetime']}
            """
        )

        map_placeholder.plotly_chart(
            fig,
            use_container_width=True
        )

        # 배속 반영
        time.sleep(1 / speed)

else:

    # 초기 빈 지도
    fig = go.Figure()

    fig.update_geos(
        projection_type="mercator",
        showcountries=True,
        showcoastlines=True,
        lataxis_range=[30, 40],
        lonaxis_range=[124, 132],
        resolution=50
    )

    fig.update_layout(
        height=700,
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    map_placeholder.plotly_chart(
        fig,
        use_container_width=True
    )