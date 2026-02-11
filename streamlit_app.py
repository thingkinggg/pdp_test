import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="실적 바 차트 레이스", layout="wide")

st.title("📊 부서별 실적 애니메이션 차트")
st.info("이 라이브러리는 ffmpeg 설치 없이도 매끄럽게 작동합니다.")

# 1. 파일 업로드
uploaded_file = st.file_uploader("엑셀 또는 CSV 파일을 업로드하세요", type=["xlsx", "csv"])

if uploaded_file:
    # 파일 읽기
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.subheader("📌 데이터 미리보기")
        st.dataframe(df.head())

        # 필수 열 확인
        required_cols = ['년도', '부서', '실적']
        if all(col in df.columns for col in required_cols):
            
            # 2. Plotly 애니메이션 차트 생성
            fig = px.bar(
                df, 
                x="실적", 
                y="부서", 
                color="부서", 
                animation_frame="년도", 
                animation_group="부서",
                orientation='h',
                # X축 범위를 데이터 최대값의 1.2배로 고정 (움직임 방지)
                range_x=[0, df['실적'].max() * 1.2], 
                title="연도별 부서 실적 변화",
                text="실적" # 막대 끝에 수치 표시
            )

            # 레이아웃 디테일 설정
            fig.update_layout(
                yaxis={'categoryorder':'total ascending'}, # 실적순 정렬
                margin=dict(l=50, r=50, t=80, b=50),
                height=600,
                showlegend=False
            )
            
            # 애니메이션 속도 조절 (1000ms = 1초)
            fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
            fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500

            # 3. 화면에 출력
            st.plotly_chart(fig, use_container_width=True)
            st.success("왼쪽 하단의 Play(▶) 버튼을 클릭해 보세요!")
            
        else:
            st.error(f"엑셀 파일에 {required_cols} 열이 포함되어 있어야 합니다.")
            
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
