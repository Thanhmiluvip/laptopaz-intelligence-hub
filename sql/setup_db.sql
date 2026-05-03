-- Kịch bản khởi tạo Cơ sở dữ liệu cho dự án LaptopAZ Tracker
-- Hệ quản trị: SQL Server

CREATE DATABASE LaptopAZ_Tracker;
GO

USE LaptopAZ_Tracker;
GO

-- 1. Bảng danh mục sản phẩm gốc
CREATE TABLE Products (
    ProductID INT PRIMARY KEY IDENTITY(1,1),
    ProductName NVARCHAR(MAX) NOT NULL,
    ProductURL NVARCHAR(MAX) NOT NULL UNIQUE
);

-- 2. Bảng lưu lịch sử giá và tồn kho
CREATE TABLE TrackingLogs (
    LogID INT PRIMARY KEY IDENTITY(1,1),
    ProductID INT FOREIGN KEY REFERENCES Products(ProductID),
    Price NVARCHAR(50),
    StockStatus NVARCHAR(100),
    ScrapedAt DATETIME DEFAULT GETDATE()
);