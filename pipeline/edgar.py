import requests
from bs4 import BeautifulSoup

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


def get_filings(cik: str, form_type: str = "8-K", limit: int = 5) -> list:
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    data = response.json()
    recent = data["filings"]["recent"]

    forms = recent["form"]
    dates = recent["filingDate"]
    accessions = recent["accessionNumber"]

    results = []
    for form, date, accession in zip(forms, dates, accessions):
        if form == form_type:
            results.append({
                "form": form,
                "date": date,
                "accession": accession,
            })
        if len(results) >= limit:
            break

    return results

def get_filing_docs(cik: str, accession: str) -> list:
    accession_clean = accession.replace("-", "")
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_clean}/index.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    data = response.json()
    documents = data["directory"]["item"]

    return documents

def get_exhibit_url(cik: str, accession: str, docs: list) -> str:
    accession_clean = accession.replace("-", "")
    base_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_clean}/"

    for doc in docs:
        name = doc["name"].lower()
        if "ex99" in name and name.endswith(".htm"):
            return base_url + doc["name"]

    raise ValueError("No exhibit found in this filing")

def get_exhibit_text(url: str) -> str:
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(separator="\n")


if __name__ == "__main__":
    cik = get_cik("AAPL")
    filings = get_filings(cik)

    first = filings[0]
    docs = get_filing_docs(cik, first["accession"])
    url = get_exhibit_url(cik, first["accession"], docs)
    text = get_exhibit_text(url)
    print(text[:500])