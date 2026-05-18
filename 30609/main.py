import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import os

# 1. 페이지 설정
st.set_page_config(page_title="태풍 매미 경로 추적 시스템", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 실제 데이터 로드 및 전처리
@st.cache_data
def load_maemi_actual_data():
    raw_data = {
        "lat_raw": ["16N", "18.9N", "20.1N", "22.4N", "23.7N", "24.3N", "25.3N", "25.8N", "26.8N", "28.5N", "29.5N", "30.5N", "31.6N", "32.7N", "33.8N", "35.1N", "35.8N", "37.1N", "37.8N", "38.6N", "40.5N", "42.3N", "46N"],
        "lon_raw": ["141.5E", "136.9E", "132.9E", "129.4E", "127.4E", "126E", "125.1E", "125.2E", "125.4E", "125.8E", "126.1E", "126.5E", "126.7E", "127E", "127.5E", "128.4E", "128.7E", "129.7E", "130.7E", "131.7E", "134.5E", "138.1E", "144E"],
        "grade": ["TS", "TS", "STS", "TY", "TY", "TY", "TY", "TY", "TY", "TY", "TY", "TY", "TY", "TY", "TY", "TY", "TY", "STS", "STS", "STS", "STS", "STS", "null"]
    }
    df = pd.DataFrame(raw_data)
    
    # 위도/경도 변환
    df['lat'] = df['lat_raw'].str.replace('N', '').astype(float)
    df['lon'] = df['lon_raw'].str.replace('E', '').astype(float)
    
    # 등급별 가상 풍속 매칭
    grade_speed = {"TY": 55, "STS": 30, "TS": 20, "null": 10}
    df['wind_speed'] = df['grade'].map(grade_speed)
    
    # 시간대 생성 (에러 방지를 위해 간격 조정 혹은 시작일 조정)
    # 23개의 데이터를 12시간 간격으로 배치하여 전체 기간을 확보합니다.
    df['timestamp'] = pd.date_range(start="2003-09-06", periods=len(df), freq='12h') 
    
    return df

df_maemi = load_maemi_actual_data()

# 3. 사이드바: 날짜 및 시간 선택
st.sidebar.title("📅 태풍 타임라인 설정")

# 데이터의 실제 날짜 범위 추출
min_ts = df_maemi['timestamp'].min().to_pydatetime()
max_ts = df_maemi['timestamp'].max().to_pydatetime()

# 🔥 해결 포인트: value를 min_ts로 설정하여 범위를 절대 벗어나지 않게 합니다.
selected_date = st.sidebar.date_input(
    "날짜 선택",
    value=min_ts.date(), # 시작 날짜로 기본값 설정
    min_value=min_ts.date(),
    max_value=max_ts.date()
)
selected_time = st.sidebar.slider("시간 선택 (24H)", 0, 23, 12)

# 선택된 시점 계산
target_dt = datetime.combine(selected_date, datetime.min.time()).replace(hour=selected_time)

# 현재 시점 및 과거 경로 추출
current_data = df_maemi[df_maemi['timestamp'] <= target_dt].tail(1)
past_path_data = df_maemi[df_maemi['timestamp'] <= target_dt]

# 4. 레이아웃 구성
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"🚩 태풍 매미 위치 시각화 ({target_dt})")
    m = folium.Map(location=[34, 128], zoom_start=5)
    
    # 전체 궤적
    folium.PolyLine(df_maemi[['lat', 'lon']].values.tolist(), color="gray", weight=1, opacity=0.4, dash_array='5').add_to(m)
    
    if not current_data.empty:
        # 이동 경로
        folium.PolyLine(past_path_data[['lat', 'lon']].values.tolist(), color="blue", weight=3).add_to(m)
        
        row = current_data.iloc[0]
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=15, color="red", fill=True, fill_color="red",
            popup=f"{row['grade']} ({row['lat_raw']}, {row['lon_raw']})"
        ).add_to(m)
    else:
        st.info("해당 시간에는 태풍 데이터가 없습니다. 날짜를 조정해 보세요.")
        
    st_folium(m, width=900, height=600)

with col2:
    st.subheader("📊 상세 정보")
    if not current_data.empty:
        row = current_data.iloc[0]
        st.metric("현재 등급", row['grade'])
        st.metric("추정 풍속", f"{row['wind_speed']} m/s")
        
        # 이미지 로직
        img_name = "extreme.png" if row['grade'] == "TY" else "strong.png" if row['grade'] == "STS" else "medium.png"
        img_path = os.path.join(BASE_DIR, "images", img_name)
        
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.warning(f"{img_name} 파일이 없습니다.")
        damage_img = (
            "typhoon_ty.png" if row['grade'] == "TY"
            else "typhoon_sts.png" if row['grade'] == "STS"
            else "typhoon_ts.png"
        )

        damage_path = os.path.join(BASE_DIR, "damage_images", damage_img)

        st.subheader("🌀 예상 피해 규모")

        if os.path.exists(damage_path):
            st.image(
                damage_path,
                caption=f"{row['grade']} 등급 예상 피해",
                use_container_width=True
            )
    else:
        st.write("관측 전입니다.")