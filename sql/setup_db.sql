-- =========================================================
-- Database Initialization Script for LaptopAZ Tracker
-- Target RDBMS: Microsoft SQL Server
-- =========================================================

CREATE DATABASE LaptopAZ_Tracker;
GO

USE LaptopAZ_Tracker;
GO

-- 1. Core Products Table (Master Catalog)
CREATE TABLE Products (
    ProductID INT PRIMARY KEY IDENTITY(1,1),
    ProductName NVARCHAR(MAX) NOT NULL,
    ProductURL NVARCHAR(MAX) NOT NULL UNIQUE
);

-- 2. Historical Tracking Table (Price & Inventory Logs)
CREATE TABLE TrackingLogs (
    LogID INT PRIMARY KEY IDENTITY(1,1),
    ProductID INT FOREIGN KEY REFERENCES Products(ProductID),
    Price NVARCHAR(50),
    StockStatus NVARCHAR(100),
    ScrapedAt DATETIME DEFAULT GETDATE()
);
