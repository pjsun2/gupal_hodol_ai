import os
import platform
import streamlit as st
from blog_text_mining import crawl_naver_blog, text_mining


# 플랫폼에 따라 JAVA_HOME 환경 변수 설정
if platform.system() == "Windows":
    os.environ["JAVA_HOME"] = "C:/Program Files/Java/jdk-23"  # 로컬 테스트용
else:
    os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"  # Render 서버용

# PATH 환경 변수에 JAVA_HOME의 bin 디렉토리 추가
os.environ["PATH"] = os.environ["JAVA_HOME"] + "/bin:" + os.environ["PATH"]

# Streamlit 페이지 기본 설정
st.set_page_config(page_title="구팔호돌AI", layout="centered")
st.title("구팔호돌AI")
st.write("안녕하세요")

# 블로그 텍스트 마이닝 기능 UI
st.header("📂 블로그 텍스트 마이닝")
url = st.text_input("크롤링할 네이버 블로그 URL을 입력하세요")

if st.button("크롤링 및 분석 시작"):
    if url:
        st.info("블로그 내용을 크롤링 중입니다...")
        blog_content = crawl_naver_blog(url)
        if blog_content:
            st.success("크롤링 성공! 텍스트 마이닝을 시작합니다.")
            with st.spinner("텍스트 분석 중..."):
                df, graph_buffer, wc_buffer = text_mining(blog_content)
                if df is not None:
                    st.write("📊 주요 키워드 빈도 분석 결과")
                    st.dataframe(df)

                    st.write("📈 단어 빈도 그래프")
                    st.image(graph_buffer, caption="단어 빈도 그래프", use_column_width=True)

                    st.write("☁️ 워드클라우드")
                    st.image(wc_buffer, caption="워드클라우드", use_column_width=True)
                else:
                    st.error("❌ 텍스트 마이닝 과정에서 오류가 발생했습니다.")
        else:
            st.error("❌ 블로그 내용을 가져오지 못했습니다. 올바른 URL인지 확인해 주세요.")
    else:
        st.warning("❗ 블로그 URL을 입력해 주세요.")