import requests
from bs4 import BeautifulSoup
import pyodbc
import time
import schedule

# ==========================================
# PART 1: SYSTEM CONFIGURATION
# ==========================================
SERVER_NAME = r'DESKTOP-TIF51BS\SQLEXPRESS' 
DATABASE_NAME = 'LaptopAZ_Tracker'
connection_string = f'DRIVER={{SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Target category pages for scraping product links
CATEGORY_URLS = [
    'https://laptopaz.vn/laptop-moi.html',
    'https://laptopaz.vn/laptop-like-new.html',
    'https://laptopaz.vn/linh-kien-phu-kien.html'
]

# ==========================================
# PART 2: DATA PROCESSING FUNCTIONS (ETL)
# ==========================================
def save_to_db(product_name, url, price, stock):
    """Save or update product information in SQL Server"""
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

       # 1. Check if the product exists in the Products table
        cursor.execute("SELECT ProductID FROM Products WHERE ProductURL = ?", (url,))
        row = cursor.fetchone()

        if row:
            product_id = row[0]
        else:
            cursor.execute("INSERT INTO Products (ProductName, ProductURL) OUTPUT INSERTED.ProductID VALUES (?, ?)", (product_name, url))
            product_id = cursor.fetchone()[0]

      # 2. Log historical data into the TrackingLogs table
        cursor.execute("INSERT INTO TrackingLogs (ProductID, Price, StockStatus) VALUES (?, ?, ?)", (product_id, price, stock))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  [DATABASE ERROR] {e}")

def get_product_info(url):
    """Crawl product detail page to extract Price and Stock status"""
    try:
        # Add timeout to prevent bot from hanging on slow connections
        response = requests.get(url, headers=HEADERS, timeout=15) 
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract Product Name
            name_tag = soup.find('h1', class_='pd-name')
            name = name_tag.text.strip() if name_tag else "Unknown"
            
            # Extract Product Price
            price_tag = soup.find('p', class_='pd-price')
            price = price_tag.text.strip() if price_tag else "Contact for Price"
            
            # Extract Stock Status
            stock_tag = soup.find('span', class_='pd-instock')
            stock = stock_tag.text.strip() if stock_tag else "Unknown"

            # Load data into Data Warehouse
            save_to_db(name, url, price, stock)
            
            # Truncate product name for console display
            short_name = (name[:40] + '...') if len(name) > 40 else name
            print(f"  [OK] {short_name:<45} | {price:<15} | {stock}")
            
        else:
            print(f"  [HTTP ERROR {response.status_code}] {url}")
            
    except requests.exceptions.RequestException:
        print(f"  [TIMEOUT] Slow connection, skipping URL: {url}")
    except Exception as e:
        print(f"  [SYSTEM ERROR] {e}")

def get_all_product_links(category_url):
    """Scan category page to extract all product links"""
    links = []
    try:
        response = requests.get(category_url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all anchor tags (adjust class selector if HTML structure changes)
            # Broad scan to capture accurate product URLs
            a_tags = soup.find_all('a')
            for tag in a_tags:
                href = tag.get('href')
                # Filter: Ensure link ends with .html and exclude policy/news pages
                if href and href.endswith('.html') and '/tin-tuc/' not in href and '/chinh-sach' not in href:
                    if not href.startswith('http'):
                        href = 'https://laptopaz.vn' + href
                    links.append(href)
                    
        # Use set() to remove duplicate links
        return list(set(links))
    except Exception as e:
        print(f"  [ERROR] Failed to extract links from category {category_url}: {e}")
        return []

# ==========================================
# PART 3: SCHEDULING AND ORCHESTRATION
# ==========================================
def run_master_pipeline():
    print("\n" + "="*60)
    print(f" STARTING MASTER SCRAPING CYCLE: {time.strftime('%H:%M:%S %d/%m/%Y')} ")
    print("="*60)
    
    all_links = []
    
    # Step 1: Data Discovery (URL Aggregation)
    print("\n[STEP 1] SCANNING CATEGORY PAGES FOR PRODUCTS...")
    for cat_url in CATEGORY_URLS:
        print(f" -> Scanning: {cat_url}")
        links = get_all_product_links(cat_url)
        all_links.extend(links)
        print(f"    Found {len(links)} potential links.")
        time.sleep(2)

    # Remove duplicate links across all categories
    final_links = list(set(all_links))
    print(f"\n>>> TOTAL UNIQUE PRODUCTS TO PROCESS: {len(final_links)}")

    # Step 2: Data Extraction (Price & Stock)
    print("\n[STEP 2] UPDATING PRICE AND STOCK FOR EACH PRODUCT:")
    for i, url in enumerate(final_links):
        print(f"[{i+1}/{len(final_links)}]", end="")
        get_product_info(url)
        # Mandatory 3-second delay to simulate human behavior and prevent server overload
        time.sleep(3) 

    print("\n" + "="*60)
    print(f" CYCLE COMPLETED AT: {time.strftime('%H:%M:%S')} ")
    print("="*60 + "\n")

# ==========================================
# SYSTEM INITIALIZATION
# ==========================================
if __name__ == "__main__":
    # 1. Execute initial scraping cycle immediately
    run_master_pipeline()
    
    # 2. Schedule periodic automated runs (Configured for every 6 hours)
    schedule.every(6).hours.do(run_master_pipeline)
    
    print(">>> BACKGROUND BOT ACTIVE. WAITING FOR NEXT CYCLE... <<<")
    print(">>> (Press Ctrl + C to terminate the system) <<<\n")
    
    # 3. Infinite loop to maintain background processes
    while True:
        schedule.run_pending()
        time.sleep(1)
