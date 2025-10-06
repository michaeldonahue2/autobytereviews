import os
import re
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

def slugify(text: str) -> str:
    # Convert a string to a URL-friendly slug
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def fetch_best_sellers(max_items: int = 3):
    """
    Fetch the names of best-selling products from Amazon's Best Sellers list.
    Defaults to returning the top 3 items. If an error occurs, returns sample items.
    """
    if not requests or not BeautifulSoup:
        raise ImportError("Required packages 'requests' and 'beautifulsoup4' not installed")
    url = 'https://www.amazon.com/Best-Sellers/zgbs'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
                      '(KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    names = []
    # Amazon's page structure may vary; we attempt multiple selectors
    selectors = [
        'div.p13n-sc-uncoverable-faceout a.a-link-normal div.p13n-sc-truncate',
        'span.zg-text-center-align div.a-section a.a-link-normal',
        'span.aok-inline-block a.a-link-normal'
    ]
    for selector in selectors:
        elements = soup.select(selector)
        for elem in elements:
            text = elem.get_text(strip=True)
            if text and text not in names:
                names.append(text)
            if len(names) >= max_items:
                break
        if len(names) >= max_items:
            break
    return names

def generate_post_html(title: str, date_str: str, product_name: str, slug: str) -> str:
    """
    Generate a simple HTML document for a product review.
    Includes placeholder content and a link with an affiliate tag placeholder.
    """
    keywords = '+'.join(slug.split('-'))
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\">
  <title>{title}</title>
  <link rel=\"stylesheet\" href=\"styles.css\">
</head>
<body>
  <h1>{title}</h1>
  <p><em>{date_str}</em></p>
  <h2>Overview</h2>
  <p>{product_name} is trending on Amazon. This product has captured consumer interest because of its high quality and innovative features. In this review, we'll explore why it's so popular.</p>
  <h2>Key Features</h2>
  <ul>
    <li>High quality materials</li>
    <li>Excellent performance</li>
    <li>Great value for the price</li>
  </ul>
  <h2>Conclusion</h2>
  <p>If you're in the market for something new, {product_name} is worth considering. It's one of the top-selling items today.</p>
  <p><a href=\"https://www.amazon.com/s?k={keywords}&tag=YOUR_AFFILIATE_ID\">Buy on Amazon</a></p>
  <p><a href=\"index.html\">Back to Home</a></p>
</body>
</html>"""

def build_site(product_names):
    """
    Build the static site by generating HTML files for each product and an index page.
    Product pages and index are placed in the `docs` directory.
    """
    docs_dir = 'docs'
    os.makedirs(docs_dir, exist_ok=True)
    # Create base stylesheet if it doesn't exist
    style_path = os.path.join(docs_dir, 'styles.css')
    if not os.path.exists(style_path):
        with open(style_path, 'w', encoding='utf-8') as f:
            f.write("""body {font-family: Arial, sans-serif; margin: 2rem; max-width: 800px;}
 h1 {color: #333;}
 a {color: #0366d6;}
""")
    posts_info = []
    today = datetime.utcnow().strftime('%Y-%m-%d')
    for product in product_names:
        slug = slugify(product)
        filename = f"{slug}.html"
        filepath = os.path.join(docs_dir, filename)
        # Avoid overwriting existing files for repeat runs
        if not os.path.exists(filepath):
            title = f"{product} Review"
            html_content = generate_post_html(title, today, product, slug)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
        posts_info.append((product, slug, today))
    # Generate index.html
    index_path = os.path.join(docs_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
<meta charset=\"utf-8\">
<title>AutoByte Reviews</title>
<link rel=\"stylesheet\" href=\"styles.css\">
</head>
<body>
<h1>AutoByte Reviews</h1>
<p>Welcome to AutoByte Reviews. Here you will find AI-generated reviews of trending products.</p>
<ul>
""")
        for product, slug, date_str in posts_info:
            f.write(f'<li><a href=\"{slug}.html\">{product} Review</a> - {date_str}</li>\n')
        f.write("""</ul>
</body>
</html>""")

def main():
    # Try to fetch best sellers; fallback to sample products
    try:
        names = fetch_best_sellers(max_items=3)
    except Exception as e:
        names = [
            "Sample Product A",
            "Sample Product B",
            "Sample Product C",
        ]
    build_site(names)

if __name__ == '__main__':
    main()
