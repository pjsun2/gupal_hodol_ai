import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
from konlpy.tag import Okt

plt.rcParams['axes.unicode_minus'] = False

# 폰트 경로 (Linux 서버 환경에 맞게 설정)
font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

# 블로그 크롤링 함수
def crawl_naver_blog(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        iframe = soup.find("iframe", id="mainFrame")
        if not iframe:
            return None

        iframe_url = "https://blog.naver.com" + iframe["src"]
        res_iframe = requests.get(iframe_url, headers={"User-Agent": "Mozilla/5.0"})
        soup_iframe = BeautifulSoup(res_iframe.text, "html.parser")
        content = soup_iframe.find("div", class_="se-main-container")

        return content.get_text(separator="\n", strip=True) if content else None

    except Exception as e:
        print("오류 발생:", e)
        return None

# 텍스트 마이닝 및 시각화 함수
def text_mining(blog_content, file_prefix="result"):
    text = re.sub(r'\n', ' ', blog_content)
    text = re.sub(r'[^가-힣\s]', '', text)

    okt = Okt()
    nouns = okt.nouns(text)

    # 불용어 정의
    stopwords = set(["것", "저", "수", "등", "있다", "하다", "되다", "한", "하고", "하다"])
    nouns = [word for word in nouns if word not in stopwords and len(word) > 1]

    word_counts = Counter(nouns)
    df = pd.DataFrame(word_counts.most_common(20), columns=["단어", "빈도"])

    # 단어 빈도 그래프 저장
    plt.figure(figsize=(10, 5))
    plt.bar(df["단어"], df["빈도"])
    plt.title("블로그 주요 키워드", fontsize=15)
    plt.xlabel("단어", fontsize=12)
    plt.ylabel("빈도수", fontsize=12)
    plt.xticks(rotation=45)
    freq_image_path = f"assets/{file_prefix}_word_frequency.png"
    plt.savefig(freq_image_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 워드클라우드 생성 및 저장
    wordcloud = WordCloud(font_path=font_path, background_color="white", width=800, height=400)
    wordcloud.generate_from_frequencies(word_counts)
    wordcloud_image_path = f"assets/{file_prefix}_wordcloud.png"
    wordcloud.to_file(wordcloud_image_path)

    return df, freq_image_path, wordcloud_image_path
