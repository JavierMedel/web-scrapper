import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime
import time

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)
    return driver

def scrape_page(driver, url):
    try:
        print(f"Fetching page: {url}")
        driver.get(url)

        # Wait for the page to load
        time.sleep(5)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        print("Parsing content...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        recipes = []
        
        for card in soup.find_all('div', class_='card'):
            # Extract Recipe Name
            name_tag = card.find('h2')
            name = name_tag.text.strip() if name_tag else "No name"

            # Extract Description
            description_tag = card.find('div', class_='text-primary-800')
            description = description_tag.text.strip() if description_tag else "No description"

            # Extract Recipe URL and PDF URL
            recipe_url = None
            pdf_url = None
            for link in card.find_all('a', {'href': True}):
                href = link['href']
                if 'recipes/' in href:
                    recipe_url = urljoin(url, href)
                elif href.endswith('.pdf'):
                    pdf_url = urljoin(url, href)

            # Extract Image URL
            image_tag = card.find('img')
            image_url = urljoin(url, image_tag['src']) if image_tag and 'src' in image_tag.attrs else None

            if recipe_url or pdf_url:
                recipes.append({
                    'name': name,
                    'description': description,
                    'recipe_url': recipe_url,
                    'pdf_url': pdf_url,
                    'image_url': image_url
                })

        return recipes
    except Exception as e:
        print(f"Error scraping the page: {e}")
        return []

def save_links(recipes, page_number, region):
    filename = f"{region}/recipe_links_page_{page_number}.json"
    data = {
        'timestamp': datetime.now().isoformat(),
        'total_recipes': len(recipes),
        'source_url': f'https://hfresh.info/{region}',
        'recipes': recipes
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(recipes)} recipes to {filename}")

def main():
    region = 'es-es' 
    page_number = 367
    base_url = f"https://hfresh.info/{region}?page={{}}"
    driver = setup_driver()

    try:
        while True:
            url = base_url.format(page_number)
            recipes = scrape_page(driver, url)
            if not recipes:
                break  # Stop if no recipes are found, assuming no more pages
            save_links(recipes, page_number, region)
            page_number += 1
            time.sleep(2)  # Delay between requests
    finally:
        driver.quit()
        print("Scraping complete.")

if __name__ == "__main__":
    main()
