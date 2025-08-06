import streamlit as st
import pandas as pd
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load data
def load_data():
    brastemp_df = pd.read_parquet("Brastemp_products_info.parquet")
    electrolux_df = pd.read_parquet("electrolux_products_info.parquet")
    return brastemp_df, electrolux_df

def display_product_summary(df):
    st.write("### 요약 통계")
    st.write("브랜드 분포:")
    st.write(df['brand'].value_counts())
    st.write("카테고리 분포:")
    st.write(df['categories'].value_counts().head(10))

def show_usp_comparison(product_name, brastemp_df, electrolux_df):
    st.write("### PDP 문구 비교 분석")

    def extract_usp_text(df, brand):
        row = df[df['product_name'].str.contains(product_name, case=False, na=False, regex=False)]
        if not row.empty:
            text = row.iloc[0]['usp_details']
            return text, brand
        return "", brand

    b_text, b_title = extract_usp_text(brastemp_df, 'Brastemp')
    e_text, e_title = extract_usp_text(electrolux_df, 'Electrolux')

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Brastemp - {b_title}")
        st.text(b_text)
    with col2:
        st.subheader(f"Electrolux - {e_title}")
        st.text(e_text)

    # Simple similarity comparison
    if b_text.strip() and e_text.strip():
        vectorizer = TfidfVectorizer().fit_transform([b_text, e_text])
        sim_score = cosine_similarity(vectorizer[0:1], vectorizer[1:2])[0][0]
        st.success(f"🔍 USP 유사도 분석 결과: {sim_score:.2f} (cosine similarity)")

# === Streamlit UI ===
st.set_page_config(page_title="PDP USP 분석 도구", layout="wide")
st.title("📊 브라질 냉장고 PDP USP 분석 대시보드")

brastemp_df, electrolux_df = load_data()

# 탭 구성
selected_tab = st.sidebar.radio("기능 선택", ["요약 보기", "제품별 USP 비교", "기능 추천 (추가)", "데이터 보기"])

if selected_tab == "요약 보기":
    st.header("✅ 데이터 요약")
    display_product_summary(pd.concat([brastemp_df, electrolux_df], axis=0))

elif selected_tab == "제품별 USP 비교":
    st.header("🔍 제품명으로 PDP USP 비교")
    all_names = list(brastemp_df['product_name'].dropna().unique()) + list(electrolux_df['product_name'].dropna().unique())
    selected_name = st.selectbox("제품명 키워드 입력 또는 선택", sorted(set(all_names)))
    if selected_name:
        show_usp_comparison(selected_name, brastemp_df, electrolux_df)

elif selected_tab == "기능 추천 (추가)":
    st.header("✨ LLM 기반 추천 기능")
    selected_row = st.selectbox("Brastemp 제품 중 하나 선택", brastemp_df['product_name'])
    selected_usp = brastemp_df[brastemp_df['product_name'] == selected_row]['usp_details'].values[0]
    st.markdown("#### 선택한 제품의 USP:")
    st.text(selected_usp)
    
    st.markdown("#### 🤖 LLM 분석 결과 (예시):")
    st.info("이 제품은 물 디스펜서, Blue Touch 온도 조절, 유연한 선반 구조를 통해 사용 편의성과 실용성을 강조하고 있습니다. 경쟁사 제품 대비 디스펜서 기능이 더 강조되어 있음.")

elif selected_tab == "데이터 보기":
    st.header("🧾 원본 데이터 보기")
    brand_choice = st.radio("브랜드 선택", ["Brastemp", "Electrolux"])
    if brand_choice == "Brastemp":
        st.dataframe(brastemp_df)
    else:
        st.dataframe(electrolux_df)
