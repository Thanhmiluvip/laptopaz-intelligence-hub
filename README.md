# LaptopAZ Intelligence Hub
An Automated End-to-End Data Pipeline for Real-time Market Price and Inventory Monitoring.

## Project Overview
This system is designed to automate the process of tracking laptop prices and availability at LaptopAZ (Ha Dong Branch). By implementing a complete ETL (Extract, Transform, Load) pipeline, the project replaces manual data entry with a high-performance, real-time monitoring solution, ensuring data accuracy for business decision-making.

---

## Technical Architecture
The system consists of four primary layers:
1. **Data Ingestion Layer:** A Python-based crawler utilizing Requests and BeautifulSoup4 to extract unstructured data from target domains.
2. **Storage Layer:** A relational database schema implemented in Microsoft SQL Server to maintain data integrity and historical logs.
3. **Application Layer (API):** A RESTful API built with FastAPI to serve processed data with low latency.
4. **Presentation Layer (Dashboard):** A modern, responsive web interface utilizing Glassmorphism principles and asynchronous JavaScript for data visualization.

---

## Tech Stack
* **Programming Language:** Python 3.10+
* **Backend Framework:** FastAPI (Asynchronous Server Gateway Interface)
* **Database:** Microsoft SQL Server (RDBMS)
* **Web Technologies:** HTML5, CSS3 (Modern Flexbox/Grid), JavaScript (ES6+)
* **Libraries:** BeautifulSoup4, Requests, PyODBC, Schedule, Lucide
* **Deployment Tools:** Ngrok (Secure Tunneling), Virtualenv

---

## Directory Structure
```text
laptopaz-tracker/
├── src/
│   ├── api_server.py      # REST API Implementation
│   └── scraper.py         # ETL & Automated Scheduling Logic
├── sql/
│   └── setup_db.sql       # Database Schema & Initialization
├── web/
│   └── index.html         # Frontend Intelligence Dashboard
├── .gitignore             # Git exclusion rules
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
Installation and Setup
1. Environment Configuration
Ensure you have Python and Microsoft SQL Server installed. Clone the repository and install dependencies:
git clone [https://github.com/Thanhmiluvip/laptopaz-intelligence-hub.git](https://github.com/Thanhmiluvip/laptopaz-intelligence-hub.git)
cd laptopaz-tracker
pip install -r requirements.txt
2. Database Initialization
Execute the SQL script located in sql/setup_db.sql within your SQL Server Management Studio (SSMS) to create the necessary tables and relationships.

3. Executing the Backend API
Navigate to the root directory and start the FastAPI server:
uvicorn src.api_server:app --reload
4. Running the Scraper
Open a separate terminal to initiate the data collection process:
python src/scraper.py
Core Functionalities
Automated Orchestration: The scraper is programmed to update data every 6 hours automatically.

Smart Filtering: Advanced JavaScript-based search and price sorting functionality.

Data Cleansing: Automated removal of inconsistent entries (Contact for Price/Out of Stock).

Cross-Origin Resource Sharing (CORS): Fully configured for secure frontend-backend communication.

About the Author
Tran Dang Thanh

Academic Advisor at Posts and Telecommunications Institute of Technology (PTIT).

Branch Manager at LaptopAZ (Ha Dong Branch).

Expertise: Data Engineering, Big Data System Architecture, Backend Development.

Copyright © 2026 Tran Dang Thanh. All rights reserved.