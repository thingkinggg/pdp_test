import streamlit as st
import pandas as pd
import bar_chart_race as bcr
import tempfile

st.title("📊 부서별 실적 바 차트 레이스")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    try:
        # 1. 데이터 타입 강제 변환 (숫자가 아닌 것은 NaN으로, 그 후 0으로 채움)
        df['실적'] = pd.to_numeric(df['실적'], errors='coerce').fillna(0)
        
        # 2. 피벗 테이블 생성 (Long -> Wide)
        df_reshaped = df.pivot(index='년도', columns='부서', values='실적')
        
        # 3. 인덱스(년도) 정렬
        df_reshaped = df_reshaped.sort_index()

        st.write("차트 생성 준비 완료:", df_reshaped.head())

        if st.button("애니메이션 생성"):
            with st.spinner("비디오 파일 변환 중... (데이터 양에 따라 1~2분 소요될 수 있습니다)"):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmpfile:
                    # n_bars는 부서 개수보다 많으면 안 됩니다.
                    num_departments = len(df_reshaped.columns)
                    
                    bcr.bar_chart_race(
                        df=df_reshaped,
                        filename=tmpfile.name,
                        title='연도별 부서 실적 변화',
                        orientation='h',
                        sort='desc',
                        n_bars=min(10, num_departments), # 최대 10개 혹은 부서 수만큼
                        fixed_max=True,
                        steps_per_period=10, # 부드러운 전환을 위해 설정
                        period_length=1000
                    )
                    
                    video_file = open(tmpfile.name, 'rb')
                    st.video(video_file.read())
                    st.success("완료되었습니다!")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        st.info("데이터 구조를 확인해주세요. (필수 열: 년도, 부서, 실적)")
