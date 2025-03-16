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
        time.sleep(5)  # Allow time for page load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        print("Parsing content...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        recipes = []
        
        for card in soup.find_all('div', class_='card'):
            name_tag = card.find('h2')
            name = name_tag.text.strip() if name_tag else "No name"
            
            description_tag = card.find('div', class_='text-primary-800')
            description = description_tag.text.strip() if description_tag else "No description"
            
            recipe_url = None
            pdf_url = None
            
            for link in card.find_all('a', {'href': True}):
                href = link['href']
                if 'recipes/' in href:
                    recipe_url = urljoin(url, href)
                elif href.endswith('.pdf'):
                    pdf_url = urljoin(url, href)
            
            if recipe_url or pdf_url:
                recipes.append({
                    'name': name,
                    'description': description,
                    'recipe_url': recipe_url,
                    'pdf_url': pdf_url
                })
        
        return recipes
    except Exception as e:
        print(f"Error scraping the page: {e}")
        return []

def save_links(recipes, page_number):
    filename = f"recipes_data/recipe_links_page_{page_number}.json"
    data = {
        'timestamp': datetime.now().isoformat(),
        'total_recipes': len(recipes),
        'source_url': 'https://hfresh.info/ca-en',
        'recipes': recipes
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(recipes)} recipes to {filename}")

def main():
    base_url = "https://hfresh.info/ca-en?page={}"
    driver = setup_driver()
    
    try:
        for page_number in range(0, 1450):  # Adjust range as needed
            url = base_url.format(page_number)
            recipes = scrape_page(driver, url)
            save_links(recipes, page_number)
            time.sleep(2)
    finally:
        driver.quit()
        print("Scraping complete.")

if __name__ == "__main__":
    main()
