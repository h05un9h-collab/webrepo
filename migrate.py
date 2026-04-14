# migrate.py
import os
import re
from bs4 import BeautifulSoup

SITE_TITLE = "GRUND'S HOME"
NAV_LINKS = {'review': 'REVIEW', 'news': 'NEWS', 'misc': 'MISC'}
NEWS_YEARS = ['1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003']

def read_html(path):
    """EUC-KR 파일을 읽어 유니코드 문자열로 반환"""
    with open(path, 'rb') as f:
        return f.read().decode('euc-kr', errors='replace')

def slugify(name):
    """밴드명 → URL 슬러그 (소문자, 공백→밑줄)"""
    return re.sub(r'[^a-z0-9_]', '', name.lower().replace(' ', '_'))

def extract_reviews(html):
    """review.html 에서 앨범 리뷰 목록 추출.
    각 앨범 블록은 <td width="650"> 안에 있음.
    반환: [{'title', 'year', 'label', 'score', 'text'}, ...]
    """
    soup = BeautifulSoup(html, 'html.parser')
    reviews = []
    for td in soup.find_all('td', attrs={'width': '650'}):
        title_el = td.find(class_='body2')
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if not title:
            continue

        meta_el = td.find(class_='body5')
        year, label = '', ''
        if meta_el:
            meta = meta_el.get_text(strip=True).strip('()')
            parts = meta.split(',', 1)
            year = parts[0].strip()
            label = parts[1].strip() if len(parts) > 1 else ''

        score_el = td.find(class_='body4')
        score = score_el.get_text(strip=True) if score_el else ''

        text_el = td.find(class_='body1')
        text = text_el.get_text(separator='\n', strip=True) if text_el else ''

        reviews.append({'title': title, 'year': year, 'label': label,
                        'score': score, 'text': text})
    return reviews

def extract_news_entries(html):
    """연도별 뉴스 파일에서 밴드 뉴스 항목 추출.
    bgcolor="#666666" 행이 밴드명, 다음 행이 뉴스 내용.
    반환: [{'band', 'content'}, ...]
    """
    soup = BeautifulSoup(html, 'html.parser')
    entries = []
    rows = soup.find_all('tr')
    i = 0
    while i < len(rows):
        td = rows[i].find('td', attrs={'bgcolor': '#666666'})
        if td:
            band = td.get_text(strip=True)
            if i + 1 < len(rows):
                content_td = rows[i + 1].find('td')
                content = content_td.get_text(strip=True) if content_td else ''
                if band:
                    entries.append({'band': band, 'content': content})
                i += 2
            else:
                i += 1
        else:
            i += 1
    return entries
