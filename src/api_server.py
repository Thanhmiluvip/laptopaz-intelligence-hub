from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Thư viện mới thêm
import pyodbc

app = FastAPI(title="LaptopAZ Tracker API")

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SQL Server Connection Configuration ---
SERVER_NAME = r'DESKTOP-TIF51BS\SQLEXPRESS' 
DATABASE_NAME = 'LaptopAZ_Tracker'
connection_string = f'DRIVER={{SQL Server}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;'

def get_db_connection():
    return pyodbc.connect(connection_string)

@app.get("/api/inventory")
def get_current_inventory():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT p.ProductID, p.ProductName, p.ProductURL, t.Price, t.StockStatus, t.ScrapedAt
            FROM Products p
            CROSS APPLY (
                SELECT TOP 1 Price, StockStatus, ScrapedAt
                FROM TrackingLogs
                WHERE ProductID = p.ProductID
                ORDER BY ScrapedAt DESC
            ) t
        """
        cursor.execute(query)
        
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
            
        conn.close()
        return {"status": "success", "data": results}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
