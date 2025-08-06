import streamlit as st
import pandas as pd
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import AzureChatOpenAI

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

    # 제품 비교 UI
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

    # === 기능 1: SPEC 비교 ===
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

    # === 기능 2: USP 요약 (LangChain + Azure OpenAI)
    with st.expander("📌 USP 분석 결과 요약 (Azure OpenAI 기반)"):
        required_keys = ["AZURE_API_KEY", "AZURE_ENDPOINT", "DEPLOYMENT_NAME"]

        # LangChain LLM 설정
        llm = AzureChatOpenAI(
            openai_api_key="e80449f0e6f345bf8311a3f48004f3ba",
            azure_endpoint="https://dhnp.openai.azure.com/",
            deployment_name="gpt-4o",
            api_version="2024-02-01",
            temperature=0
            )

        template = """
            다음은 Brastemp 및 Electrolux의 냉장고 제품의 USP 목록입니다.
            Brastemp:
            {br_usp}

            Electrolux:
            {el_usp}

            두 제품의 특징을 비교하고, 주요 차이점을 요약해 주세요. 
            """
        prompt = PromptTemplate(
                input_variables=["br_usp", "el_usp"],
                template=template.strip()
            )

        chain = LLMChain(llm=llm, prompt=prompt)
        summary = chain.run(br_usp=br_row['usp_details'], el_usp=el_row['usp_details'])

        st.markdown("### ✅ 요약 결과")
        st.write(summary)

else:
    st.info("좌측 사이드바에서 Brastemp, Electrolux 데이터를 업로드하세요.")
