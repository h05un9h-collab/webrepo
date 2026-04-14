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

# ─── 렌더 함수 ───────────────────────────────────────────────

def nav_html(depth=0):
    """depth: 루트=0, review/=1, review/band/=2, news/=1, misc/=1"""
    prefix = '../' * depth
    return f'''<nav class="nav">
  <div class="nav-inner">
    <a href="{prefix}index.html" class="nav-logo">{SITE_TITLE}</a>
    <div class="nav-links">
      <a href="{prefix}review/">REVIEW</a>
      <a href="{prefix}news/">NEWS</a>
      <a href="{prefix}misc/">MISC</a>
    </div>
  </div>
</nav>'''

def footer_html():
    return '''<footer class="footer">
  <div class="container">
    <p class="footer-text">GRUND\'S HOME · ARCHIVED 2003–2005</p>
  </div>
</footer>'''

def page_wrap(title, content, depth=0):
    prefix = '../' * depth
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} · GRUND\'S HOME</title>
  <link rel="stylesheet" href="{prefix}assets/css/main.css">
  <link rel="stylesheet" href="{prefix}assets/css/components.css">
</head>
<body>
{nav_html(depth)}
{content}
{footer_html()}
<script src="{prefix}assets/js/nav.js"></script>
</body>
</html>'''

def render_band_page(band_slug, reviews):
    """밴드 상세 페이지 (depth=2: review/band/)"""
    band_display = band_slug.replace('_', ' ').upper()
    albums_html = ''
    for r in reviews:
        score_html = f'<p class="album-score">{r["score"]}</p>' if r['score'] else ''
        text_html = ''.join(
            f'<p>{line}</p>' for line in r['text'].split('\n') if line.strip()
        )
        meta = r['year']
        if r['label']:
            meta += f' · {r["label"]}'
        albums_html += f'''  <div class="album-block">
    <h3 class="album-title">{r["title"]}</h3>
    <p class="album-meta">{meta}</p>
    {score_html}
    <div class="album-review">{text_html}</div>
  </div>\n'''

    content = f'''<div class="container">
  <a href="../../review/" class="back-link">← BACK TO REVIEWS</a>
  <div class="band-header">
    <div class="section-label">REVIEW</div>
    <h1 class="band-name">{band_display}</h1>
  </div>
{albums_html}</div>'''
    return page_wrap(band_display, content, depth=2)

# ─── 생성 함수 ───────────────────────────────────────────────

def generate_review_pages(repo_root):
    """new_version/review/ 아래 모든 밴드 리뷰 페이지 생성.
    반환: [{'slug', 'first_review'}, ...]
    """
    review_src = os.path.join(repo_root, 'new_version', 'review')
    bands = []
    for band_slug in sorted(os.listdir(review_src)):
        src_path = os.path.join(review_src, band_slug, 'review.html')
        if not os.path.isfile(src_path):
            continue
        html = read_html(src_path)
        reviews = extract_reviews(html)
        if not reviews:
            continue
        out_dir = os.path.join(repo_root, 'review', band_slug)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(render_band_page(band_slug, reviews))
        bands.append({'slug': band_slug, 'first_review': reviews[0]})
        print(f'  ✓ review/{band_slug}/index.html')
    return bands


if __name__ == '__main__':
    import sys
    repo_root = sys.argv[1] if len(sys.argv) > 1 else '.'
    print('Generating review pages...')
    bands = generate_review_pages(repo_root)
    print(f'Done: {len(bands)} band pages')
