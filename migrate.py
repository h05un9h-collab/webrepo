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
    if not os.path.isdir(review_src):
        raise FileNotFoundError(f'Source directory not found: {review_src}')
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


def render_review_index(bands):
    """밴드 목록 페이지 (depth=1: review/)"""
    cards_html = ''.join(
        f'<a href="{b["slug"]}/" class="review-card">'
        f'<span class="review-card-band">{b["slug"].replace("_", " ").upper()}</span>'
        f'</a>\n'
        for b in bands
    )
    content = f'''<div class="container">
  <div class="hero">
    <div class="section-label">ALL REVIEWS — {len(bands)} BANDS</div>
  </div>
  <div class="review-grid">
{cards_html}  </div>
</div>'''
    return page_wrap('REVIEWS', content, depth=1)

def generate_review_index(repo_root, bands):
    out_path = os.path.join(repo_root, 'review', 'index.html')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(render_review_index(bands))
    print('  ✓ review/index.html')

def render_news_year(year, entries):
    """연도별 뉴스 페이지 (depth=1: news/)"""
    if entries:
        entries_html = ''.join(
            f'<div class="news-entry">'
            f'<p class="news-band">{e["band"]}</p>'
            f'<p class="news-content">{e["content"]}</p>'
            f'</div>\n'
            for e in entries
        )
    else:
        entries_html = '<p style="color:var(--text-muted);font-size:11px;">기록 없음</p>'

    content = f'''<div class="container">
  <a href="index.html" class="back-link">← NEWS</a>
  <div class="hero">
    <div class="section-label">NEWS ARCHIVE</div>
    <h1 style="font-size:22px;font-weight:200;letter-spacing:4px;">{year}</h1>
  </div>
{entries_html}</div>'''
    return page_wrap(f'NEWS {year}', content, depth=1)

def render_news_index():
    """뉴스 연도 선택 인덱스 (depth=1: news/)"""
    cards_html = ''.join(
        f'<a href="{year}.html" class="year-card">'
        f'<span class="year-number">{year}</span></a>\n'
        for year in NEWS_YEARS
    )
    content = f'''<div class="container">
  <div class="hero">
    <div class="section-label">NEWS ARCHIVE</div>
    <p class="hero-sub">메탈 씬 뉴스 · 1996–2003</p>
  </div>
  <div class="year-grid">
{cards_html}  </div>
</div>'''
    return page_wrap('NEWS', content, depth=1)

def generate_news_pages(repo_root):
    os.makedirs(os.path.join(repo_root, 'news'), exist_ok=True)
    for year in NEWS_YEARS:
        src = os.path.join(repo_root, 'charts', f'{year}.html')
        entries = []
        if os.path.isfile(src):
            entries = extract_news_entries(read_html(src))
        with open(os.path.join(repo_root, 'news', f'{year}.html'), 'w', encoding='utf-8') as f:
            f.write(render_news_year(year, entries))
        print(f'  ✓ news/{year}.html ({len(entries)} entries)')
    with open(os.path.join(repo_root, 'news', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(render_news_index())
    print('  ✓ news/index.html')

def render_misc_index():
    """misc 허브 페이지 (depth=1)"""
    content = '''<div class="container">
  <div class="hero">
    <div class="section-label">MISC</div>
    <p class="hero-sub">기타 콘텐츠</p>
  </div>
  <div class="misc-grid">
    <a href="world.html" class="misc-card">
      <p class="misc-card-title">WORLD MAP</p>
      <p class="misc-card-desc">메탈 씬 세계 지도</p>
    </a>
    <a href="tolkien.html" class="misc-card">
      <p class="misc-card-title">TOLKIEN MUSIC</p>
      <p class="misc-card-desc">톨킨 음악 가이드</p>
    </a>
    <a href="cyberblack.html" class="misc-card">
      <p class="misc-card-title">CYBERBLACK</p>
      <p class="misc-card-desc">사이버블랙 페이지</p>
    </a>
  </div>
</div>'''
    return page_wrap('MISC', content, depth=1)

def render_misc_content(title, body_text):
    """misc 서브페이지 (depth=1). body_text가 비어있으면 Flash 안내 표시"""
    if body_text.strip():
        body_html = ''.join(
            f'<p style="font-size:11px;color:var(--text-secondary);line-height:1.8;margin-bottom:12px;">{p.strip()}</p>'
            for p in body_text.split('\n') if p.strip()
        )
    else:
        body_html = '<p style="color:var(--text-muted);font-size:11px;">원본 콘텐츠는 Flash를 사용하여 현재 재생할 수 없습니다.</p>'
    content = f'''<div class="container">
  <a href="index.html" class="back-link">← MISC</a>
  <div class="hero">
    <div class="section-label">MISC</div>
    <h1 style="font-size:18px;font-weight:300;letter-spacing:3px;">{title.upper()}</h1>
  </div>
  {body_html}
</div>'''
    return page_wrap(title.upper(), content, depth=1)

def extract_misc_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    return soup.get_text(separator='\n', strip=True)

def generate_misc_pages(repo_root):
    os.makedirs(os.path.join(repo_root, 'misc'), exist_ok=True)

    with open(os.path.join(repo_root, 'misc', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(render_misc_index())
    print('  ✓ misc/index.html')

    # world — Flash 콘텐츠, 대체 텍스트 사용
    with open(os.path.join(repo_root, 'misc', 'world.html'), 'w', encoding='utf-8') as f:
        f.write(render_misc_content('World Map', ''))
    print('  ✓ misc/world.html')

    for slug, src_name, display in [
        ('tolkien', 'tolkienmusic.html', 'Tolkien Music'),
        ('cyberblack', 'cyberblack.html', 'Cyberblack'),
    ]:
        src = os.path.join(repo_root, 'misc', src_name)
        text = extract_misc_text(read_html(src)) if os.path.isfile(src) else ''
        with open(os.path.join(repo_root, 'misc', f'{slug}.html'), 'w', encoding='utf-8') as f:
            f.write(render_misc_content(display, text))
        print(f'  ✓ misc/{slug}.html')


def render_home(bands):
    """홈페이지 매거진 그리드 (depth=0: root)"""
    # Featured: soilwork (마지막 업데이트 2005/01/03), 없으면 첫 번째 밴드
    featured = next((b for b in bands if b['slug'] == 'soilwork'), bands[0] if bands else None)

    featured_html = ''
    if featured:
        r = featured['first_review']
        display = featured['slug'].replace('_', ' ').upper()
        excerpt = r['text'].replace('\n', ' ')[:200].strip()
        featured_html = f'''<div class="card-featured">
    <p class="card-featured-label">FEATURED</p>
    <p class="card-featured-band">{display}</p>
    <p class="card-featured-album">{r["title"]} · {r["year"]}</p>
    <div class="card-featured-divider"></div>
    <p class="card-featured-excerpt">{excerpt}</p>
    <a href="review/{featured["slug"]}/" class="card-featured-link">READ REVIEW →</a>
  </div>'''

    others = [b for b in bands if b['slug'] != (featured['slug'] if featured else '')][:6]
    small_cards = ''.join(
        f'<a href="review/{b["slug"]}/" class="card-small">'
        f'<p class="card-small-band">{b["slug"].replace("_"," ").upper()}</p>'
        f'<p class="card-small-album">{b["first_review"]["title"]} · {b["first_review"]["year"]}</p>'
        f'</a>\n'
        for b in others
    )

    news_years_str = ' · '.join(NEWS_YEARS)
    content = f'''<div class="container">
  <div class="hero">
    <p class="hero-label">METAL MUSIC ARCHIVE</p>
    <p class="hero-sub">리뷰 {len(bands)}개 · 뉴스 아카이브 1996–2003</p>
  </div>
  <div class="section-label">REVIEWS</div>
  <div class="magazine-grid">
{featured_html}
{small_cards}  </div>
  <div class="charts-teaser">
    <div>
      <p class="charts-teaser-label">NEWS ARCHIVE</p>
      <p class="charts-teaser-years">{news_years_str}</p>
    </div>
    <a href="news/" class="charts-teaser-link">VIEW ALL →</a>
  </div>
</div>'''
    return page_wrap("GRUND'S HOME", content, depth=0)

def generate_home(repo_root, bands):
    with open(os.path.join(repo_root, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(render_home(bands))
    print('  ✓ index.html')


if __name__ == '__main__':
    import sys
    repo_root = sys.argv[1] if len(sys.argv) > 1 else '.'
    print('Generating review pages...')
    bands = generate_review_pages(repo_root)
    print('Generating review index...')
    generate_review_index(repo_root, bands)
    print('Generating news pages...')
    generate_news_pages(repo_root)
    print('Generating misc pages...')
    generate_misc_pages(repo_root)
    print('Generating homepage...')
    generate_home(repo_root, bands)
    print(f'\nDone! {len(bands)} reviews + news + misc + home.')
