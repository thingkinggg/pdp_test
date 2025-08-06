import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import openai

st.set_page_config(page_title="PDP USP Matcher", layout="wide")

# === 파일 업로드 ===
st.sidebar.header("데이터 업로드")
brastemp_file = st.sidebar.file_uploader("Brastemp Parquet 파일", type=["parquet"])
electrolux_file = st.sidebar.file_uploader("Electrolux Parquet 파일", type=["parquet"])

@st.cache_data
def load_data(file):
    return pd.read_parquet(file)

if brastemp_file and electrolux_file:
    brastemp_df = load_data(brastemp_file)
    electrolux_df = load_data(electrolux_file)

    st.success("✅ 데이터 로드 완료")

    # 제품 선택
    selected_brastemp = st.selectbox("🔎 Brastemp 제품 선택", brastemp_df['product_name'].unique())
    br_row = brastemp_df[brastemp_df['product_name'] == selected_brastemp].iloc[0]

    # TF-IDF 유사도 기반 Electrolux 매칭
    def find_best_match(base_text, candidates):
        vectorizer = TfidfVectorizer().fit([base_text] + candidates)
        tfidf = vectorizer.transform([base_text] + candidates)
        scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        best_idx = scores.argmax()
        return best_idx, scores[best_idx]

    el_idx, sim_score = find_best_match(br_row['usp_details'], electrolux_df['usp_details'].tolist())
    el_row = electrolux_df.iloc[el_idx]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🥇 Brastemp 제품")
        st.markdown(f"**제품명:** {br_row['product_name']}")
        st.markdown(f"**가격:** R${br_row['price']:,}")
        st.markdown("**USP 목록:**")
        st.write(br_row['usp_details'])

    with col2:
        st.subheader("🤖 가장 유사한 Electrolux 제품")
        st.markdown(f"**제품명:** {el_row['product_name']}")
        st.markdown(f"**가격:** R${el_row['price']:,}")
        st.markdown(f"**유사도 점수:** {sim_score:.2f}")
        st.markdown("**USP 목록:**")
        st.write(el_row['usp_details'])

    st.divider()

    # === 추가 기능 1: SPEC 비교 ===
    with st.expander("🔍 제품 SPEC 비교"):
        br_specs = json.loads(br_row['specs'])
        el_specs = json.loads(el_row['specs'])
        spec_keys = sorted(set(br_specs.keys()).union(el_specs.keys()))

        spec_data = {
            "항목": spec_keys,
            "Brastemp": [br_specs.get(k, "") for k in spec_keys],
            "Electrolux": [el_specs.get(k, "") for k in spec_keys]
        }
        st.dataframe(pd.DataFrame(spec_data))

    # === 추가 기능 2: USP 분석 요약 ===
    with st.expander("📌 USP 분석 결과 요약 (Azure OpenAI 기반)"):
        required_keys = ["AZURE_OPENAI_KEY", "AZURE_ENDPOINT", "DEPLOYMENT_NAME"]
        if not all(k in st.secrets for k in required_keys):
            st.warning("Azure OpenAI 설정이 누락되었습니다. `.streamlit/secrets.toml`에 AZURE_API_KEY, AZURE_ENDPOINT, DEPLOYMENT_NAME를 추가하세요.")
        else:
            openai.api_type = "azure"
            openai.api_key = st.secrets["AZURE_OPENAI_KEY"]
            openai.api_base = st.secrets["AZURE_ENDPOINT"]
            openai.api_version = "2023-05-15"
            deployment_name = st.secrets["DEPLOYMENT_NAME"]

            prompt = f"""
            다음은 Brastemp 및 Electrolux의 냉장고 제품의 USP 목록입니다.
            Brastemp:
            {br_row['usp_details']}

            Electrolux:
            {el_row['usp_details']}

            이 두 제품의 특징을 비교해주시고, 어떤 차별점이 있는지 요약해 주세요. 
            """

            response = openai.ChatCompletion.create(
                engine=deployment_name,
                messages=[{"role": "user", "content": prompt}]
            )

            st.markdown(response["choices"][0]["message"]["content"])
else:
    st.info("좌측 사이드바에서 Brastemp, Electrolux 데이터를 업로드하세요.")
