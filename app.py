import streamlit as st
import os

from blog_text_mining import crawl_naver_blog, text_mining

# Render 서버의 Java (JVM) 환경 설정
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
os.environ["PATH"] = os.environ["JAVA_HOME"] + "/bin:" + os.environ["PATH"]

# Streamlit 페이지 기본 설정
st.set_page_config(page_title="구팔호돌AI", layout="centered")

st.title("구팔호돌AI")
st.write("안녕하세요")

# 블로그 텍스트 마이닝 기능
st.header("📂 블로그 텍스트 마이닝")

url = st.text_input("크롤링할 네이버 블로그 URL을 입력하세요")

if st.button("크롤링 및 분석 시작"):
    if url:
        st.info("블로그 내용을 크롤링 중입니다...")
        blog_content = crawl_naver_blog(url)

        if blog_content:
            st.success("크롤링 성공! 텍스트 마이닝을 시작합니다.")
            
            with st.spinner("텍스트 분석 중..."):
                df, freq_image_path, wordcloud_image_path = text_mining(blog_content, "blog_analysis")

                st.write("📊 주요 키워드 빈도 분석 결과")
                st.dataframe(df)

                st.write("📈 단어 빈도 그래프")
                st.image(freq_image_path, caption="단어 빈도 그래프", use_column_width=True)

                st.write("☁️ 워드클라우드")
                st.image(wordcloud_image_path, caption="워드클라우드", use_column_width=True)

        else:
            st.error("❌ 블로그 내용을 가져오지 못했습니다. 올바른 URL인지 확인해 주세요.")
    else:
        st.warning("❗ 블로그 URL을 입력해 주세요.")
