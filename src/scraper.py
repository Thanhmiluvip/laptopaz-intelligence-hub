import requests
from bs4 import BeautifulSoup
import pyodbc
import time
import schedule

# ==========================================
# PHẦN 1: CẤU HÌNH HỆ THỐNG
# ==========================================
SERVER_NAME = r'DESKTOP-TIF51BS\SQLEXPRESS' 
DATABASE_NAME = 'LaptopAZ_Tracker'
connection_string = f'DRIVER={{SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Các trang danh mục để Bot đi "săn" link sản phẩm
CATEGORY_URLS = [
    'https://laptopaz.vn/laptop-moi.html',
    'https://laptopaz.vn/laptop-like-new.html',
    'https://laptopaz.vn/linh-kien-phu-kien.html'
]

# ==========================================
# PHẦN 2: CÁC HÀM XỬ LÝ DỮ LIỆU (ETL)
# ==========================================
def save_to_db(product_name, url, price, stock):
    """Lưu hoặc cập nhật thông tin sản phẩm vào SQL Server"""
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # 1. Kiểm tra tồn tại trong bảng Products
        cursor.execute("SELECT ProductID FROM Products WHERE ProductURL = ?", (url,))
        row = cursor.fetchone()

        if row:
            product_id = row[0]
        else:
            cursor.execute("INSERT INTO Products (ProductName, ProductURL) OUTPUT INSERTED.ProductID VALUES (?, ?)", (product_name, url))
            product_id = cursor.fetchone()[0]

        # 2. Lưu lịch sử vào TrackingLogs
        cursor.execute("INSERT INTO TrackingLogs (ProductID, Price, StockStatus) VALUES (?, ?, ?)", (product_id, price, stock))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  [LỖI DATABASE] {e}")

def get_product_info(url):
    """Vào trang chi tiết sản phẩm để bóc tách Giá và Tình trạng"""
    try:
        # Thêm timeout để bot không bị treo nếu web tải chậm
        response = requests.get(url, headers=HEADERS, timeout=15) 
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tìm Tên
            name_tag = soup.find('h1', class_='pd-name')
            name = name_tag.text.strip() if name_tag else "Không xác định"
            
            # Tìm Giá
            price_tag = soup.find('p', class_='pd-price')
            price = price_tag.text.strip() if price_tag else "Liên hệ"
            
            # Tìm Trạng thái
            stock_tag = soup.find('span', class_='pd-instock')
            stock = stock_tag.text.strip() if stock_tag else "Không xác định"

            # Lưu vào Data Warehouse
            save_to_db(name, url, price, stock)
            
            # Cắt ngắn tên để in ra màn hình cho gọn
            short_name = (name[:40] + '...') if len(name) > 40 else name
            print(f"  [OK] {short_name:<45} | {price:<15} | {stock}")
            
        else:
            print(f"  [LỖI HTTP {response.status_code}] {url}")
            
    except requests.exceptions.RequestException:
        print(f"  [TIMEOUT] Mạng chậm, bỏ qua link: {url}")
    except Exception as e:
        print(f"  [LỖI HỆ THỐNG] {e}")

def get_all_product_links(category_url):
    """Quét trang danh mục để lấy tất cả link sản phẩm"""
    links = []
    try:
        response = requests.get(category_url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tìm tất cả các thẻ a chứa class p-img (hoặc tùy biến nếu cấu trúc thay đổi)
            # Quét rộng để lấy được link sản phẩm chính xác nhất
            a_tags = soup.find_all('a')
            for tag in a_tags:
                href = tag.get('href')
                # Lọc: Nếu link kết thúc bằng .html và không phải là các trang chính sách, tin tức
                if href and href.endswith('.html') and '/tin-tuc/' not in href and '/chinh-sach' not in href:
                    if not href.startswith('http'):
                        href = 'https://laptopaz.vn' + href
                    links.append(href)
                    
        # Sử dụng set() để loại bỏ các link bị trùng lặp
        return list(set(links))
    except Exception as e:
        print(f"Lỗi lấy link danh mục {category_url}: {e}")
        return []

# ==========================================
# PHẦN 3: LÊN LỊCH VÀ ĐIỀU PHỐI (ORCHESTRATION)
# ==========================================
def job_tong_the():
    print("\n" + "="*60)
    print(f" BẮT ĐẦU CHU KỲ QUÉT TỔNG THỂ: {time.strftime('%H:%M:%S %d/%m/%Y')} ")
    print("="*60)
    
    all_links = []
    
    # Bước 1: Khai phá dữ liệu (Gom link)
    print("\n[BƯỚC 1] ĐANG QUÉT CÁC TRANG DANH MỤC ĐỂ TÌM SẢN PHẨM...")
    for cat_url in CATEGORY_URLS:
        print(f" -> Đang quét: {cat_url}")
        links = get_all_product_links(cat_url)
        all_links.extend(links)
        print(f"    Tìm thấy {len(links)} link tiềm năng.")
        time.sleep(2)

    # Lọc lại toàn bộ link trùng trong cả 3 danh mục
    final_links = list(set(all_links))
    print(f"\n>>> TỔNG SỐ SẢN PHẨM CẦN KIỂM TRA THỰC TẾ: {len(final_links)}")

    # Bước 2: Bóc tách chi tiết (Cào giá)
    print("\n[BƯỚC 2] BẮT ĐẦU CẬP NHẬT GIÁ VÀ TỒN KHO TỪNG MÁY:")
    for i, url in enumerate(final_links):
        print(f"[{i+1}/{len(final_links)}]", end="")
        get_product_info(url)
        # Bắt buộc nghỉ 3 giây để mô phỏng người thật, tránh quá tải server
        time.sleep(3) 

    print("\n" + "="*60)
    print(f" CHU KỲ HOÀN TẤT VÀO LÚC: {time.strftime('%H:%M:%S')} ")
    print("="*60 + "\n")

# ==========================================
# KHỞI CHẠY HỆ THỐNG
# ==========================================
if __name__ == "__main__":
    # 1. Khởi chạy quét lần đầu tiên ngay lập tức
    job_tong_the()
    
    # 2. Lên lịch chạy tự động định kỳ (Đang cài đặt 6 tiếng / 1 lần)
    schedule.every(6).hours.do(job_tong_the)
    
    print(">>> HỆ THỐNG BOT ĐANG CHẠY NGẦM. CHỜ ĐẾN CHU KỲ TIẾP THEO... <<<")
    print(">>> (Nhấn Ctrl + C trên cửa sổ này để tắt hệ thống) <<<\n")
    
    # 3. Vòng lặp duy trì tiến trình ngầm
    while True:
        schedule.run_pending()
        time.sleep(1)