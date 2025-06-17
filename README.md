# Stock Market News Impact Analysis and Forecasting

This project provides an end-to-end data analysis and machine learning pipeline designed to measure the impact of corporate news (such as product launches or sales reports) on a stock's market performance. It also includes models trained to predict future price movements.

The case study focuses on **Toyota**, using historical financial data and news events scraped from its official newsroom.

## 📋 Project Components

The pipeline is divided into three main phases:

1.  **Data Engineering:**
    * **Database:** **Docker** is used to launch a **ClickHouse** instance, a high-performance database optimized for time-series analysis.
    * **Data Ingestion:** A script loads historical financial data (OHLCV) from the Alpha Vantage API into ClickHouse.
    * **Data Enrichment:** A web scraper (using `requests` and `BeautifulSoup`) reads a list of news URLs, extracts their publication dates, and updates the database to flag these event days.

2.  **Impact Analysis:**
    * **Descriptive Analysis:** Compares key metrics (return, volatility, volume) between "news days" and "no-news days" for a preliminary impact assessment.
    * **Event Study:** Implements a rigorous financial methodology to measure the stock's "abnormal return" around the news date, controlling for general market movements (using the S&P 500 as a proxy).

3.  **Machine Learning for Prediction:**
    * **Objective:** To predict whether the stock price will go up or down on the following day (Binary Classification).
    * **Implemented Models:** Three different architectures are trained and evaluated:
        1.  **XGBoost:** A powerful and efficient tree-based model, excellent for tabular data.
        2.  **LSTM (Long Short-Term Memory):** A recurrent neural network, ideal for capturing patterns in time sequences.
        3.  **Transformer:** A state-of-the-art deep learning architecture based on attention mechanisms, capable of capturing long-range dependencies.

## 🛠️ Tech Stack

* **Language:** Python 3
* **Database:** ClickHouse
* **Containerization:** Docker / Docker Compose
* **Core Libraries:**
    * `pandas` for data manipulation.
    * `clickhouse-driver` for database connectivity.
    * `requests` & `beautifulsoup4` for web scraping.
    * `yfinance` for downloading market index data.
    * `scikit-learn` for preprocessing and evaluation metrics.
    * `xgboost`, `tensorflow` for Machine Learning models.
    * `matplotlib` & `seaborn` for data visualization.
    * `python-dotenv` for credentials management.

## ⚙️ Setup and Installation

Follow these steps to get the project up and running:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/E-sanchez03/car-release-finance.git](https://github.com/E-sanchez03/car-release-finance.git)
    cd car-release-finance
    ```

2.  **Configure Credentials:**
    Create a file named `credenciales.env` in the project's root directory. It should contain your credentials for the database and the Alpha Vantage API.
    ```env
    # File: credenciales.env
    CH_USER=user
    CH_PASSWORD=password
    ALPHA_VANTAGE_API=YOUR_API_KEY_HERE
    ```

3.  **Launch the Database with Docker:**
    Ensure you have Docker and Docker Compose installed. Then, run:
    ```bash
    docker-compose up -d
    ```

4.  **Create a virtual environment and install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    
    pip install -r requirements.txt
    ```

## 🚀 Pipeline Execution

Run the scripts in the following order from the project's root directory.

1.  **Initialize the Database:**
    Creates the necessary database and tables.
    ```bash
    python src/1_data_pipeline/initialize_database.py
    ```

2.  **Load Financial Data:**
    Downloads data from Alpha Vantage (if not already present) and loads it into ClickHouse.
    ```bash
    python src/1_data_pipeline/load_to_clickhouse.py
    ```

3.  **Enrich Data with News:**
    Reads the `data/noticias.txt` file, scrapes the dates, and updates the database records.
    ```bash
    python src/1_data_pipeline/enrich_data.py
    ```

4.  **Perform Impact Analysis (Optional):**
    ```bash
    python src/2_analysis/analyze_impact_descriptive.py
    python src/2_analysis/analyze_impact_event_study.py
    ```

5.  **Train Machine Learning Models:**
    You can run each training script independently.
    ```bash
    python src/3_modeling/train_xgboost.py
    python src/3_modeling/train_lstm.py
    python src/3_modeling/train_transformer.py
    ```