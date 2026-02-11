import streamlit as st
import pandas as pd
import bar_chart_race as bcr
import tempfile

st.set_page_config(page_title="Excel Bar Chart Race", layout="wide")

st.title("📊 엑셀 데이터 바 차트 레이스")
st.write("엑셀 파일을 업로드하면 시간에 따른 순위 변화를 애니메이션으로 보여줍니다.")

# 1. 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일을 선택하세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    # 데이터 로드
    df = pd.read_excel(uploaded_file)
    
    # 첫 번째 열을 인덱스(시간축)로 설정
    time_col = df.columns[0]
    df = df.set_index(time_col)
    
    st.subheader("📌 업로드된 데이터 미리보기")
    st.dataframe(df.head())

    if st.button("애니메이션 생성 시작"):
        with st.spinner("비디오를 생성 중입니다. 잠시만 기다려 주세요..."):
            # 임시 파일 경로 설정 (비디오 저장용)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmpfile:
                # 바 차트 레이스 생성
                bcr.bar_chart_race(
                    df=df,
                    filename=tmpfile.name,
                    orientation='h',
                    sort='desc',
                    n_bars=10,
                    fixed_max=True,
                    steps_per_period=10,
                    period_length=500,
                    title=f'{time_col}별 변화 추이'
                )
                
                # 비디오 재생
                video_file = open(tmpfile.name, 'rb')
                video_bytes = video_file.read()
                st.video(video_bytes)
                st.success("생성이 완료되었습니다!")
