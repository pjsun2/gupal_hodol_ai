import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
from konlpy.tag import Okt
import io

plt.rcParams['axes.unicode_minus'] = False

# 폰트 경로 (Linux 서버 환경에 맞게 설정)
font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

# 🔍 네이버 블로그 크롤링 함수 정의
def crawl_naver_blog(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"❌ 네이버 블로그 접근 실패: {res.status_code}")
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        iframe = soup.find("iframe", id="mainFrame")
        if not iframe:
            print("❌ 블로그 본문을 찾을 수 없습니다. iframe 태그가 없습니다.")
            return None

        iframe_src = iframe.get("src")
        if not iframe_src:
            print("❌ iframe 태그에 src 속성이 없습니다.")
            return None

        # iframe_src가 이미 절대 URL이면 그대로 사용, 아니라면 베이스 URL을 붙임
        if iframe_src.startswith("http"):
            iframe_url = iframe_src
        else:
            iframe_url = "https://blog.naver.com" + iframe_src

        res_iframe = requests.get(iframe_url, headers=headers, timeout=10)
        if res_iframe.status_code != 200:
            print(f"❌ iframe 접근 실패: {res_iframe.status_code}")
            return None

        soup_iframe = BeautifulSoup(res_iframe.text, "html.parser")
        # 기본 콘텐츠 추출 시도
        content = soup_iframe.find("div", class_="se-main-container")
        if not content:
            # 대체 방식: 'postViewArea' 클래스를 가진 div
            content = soup_iframe.find("div", class_="postViewArea")
        if not content:
            print("❌ 블로그 본문 콘텐츠를 찾을 수 없습니다.")
            return None

        text = content.get_text(separator="\n", strip=True)
        return text
    except Exception as e:
        print("🚨 크롤링 오류 발생:", e)
        return None

# 🔍 텍스트 마이닝 및 시각화 함수
def text_mining(blog_content):
    try:
        # 불필요한 개행 제거 및 한글 외 문자 제거
        text = re.sub(r'\n', ' ', blog_content)
        text = re.sub(r'[^가-힣\s]', '', text)

        # Okt 객체 생성 (여기서 konlpy가 JVM을 초기화합니다)
        okt = Okt()
        nouns = okt.nouns(text)

        # 불용어 집합 (중복 항목 제거)
        stopwords = {"것", "저", "수", "등", "있다", "하다", "되다", "한", "하고"}
        nouns = [word for word in nouns if word not in stopwords and len(word) > 1]

        word_counts = Counter(nouns)
        df = pd.DataFrame(word_counts.most_common(20), columns=["단어", "빈도"])

        # 단어 빈도 그래프 생성 및 메모리 버퍼에 저장
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(df["단어"], df["빈도"])
        plt.title("블로그 주요 키워드", fontsize=15)
        plt.xlabel("단어", fontsize=12)
        plt.ylabel("빈도수", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()

        graph_buffer = io.BytesIO()
        plt.savefig(graph_buffer, format="png")
        graph_buffer.seek(0)
        plt.close()

        # 워드클라우드 생성 및 메모리 버퍼에 저장
        wordcloud = WordCloud(font_path=font_path, background_color="white", width=800, height=400)
        wordcloud.generate_from_frequencies(word_counts)
        wc_buffer = io.BytesIO()
        wordcloud.to_image().save(wc_buffer, format="png")
        wc_buffer.seek(0)

        return df, graph_buffer, wc_buffer
    except Exception as e:
        print("🚨 텍스트 마이닝 오류 발생:", e)
        return None, None, None
