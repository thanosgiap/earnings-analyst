import requests

HEADERS = {"User-Agent": "earnings-analyst 1.dim.nm.e2@gmail.com"}

def get_cik(ticker: str) -> str:
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    data = response.json()
    
    for entry in data.values():
        if entry["ticker"] == ticker.upper():
            return str(entry["cik_str"]).zfill(10)
    
    raise ValueError(f"Ticker '{ticker}' not found")


if __name__ == "__main__":
    cik = get_cik("NVDA")
    print(cik)