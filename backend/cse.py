import os
import requests
from dotenv import load_dotenv

load_dotenv()

def google_search(query, num=4):
    """
    Perform a Google Custom Search query using API key and CSE ID from env vars.
    
    :param query: Search query string
    :param num: Number of results (max 10 per request)
    :return: List of results (title, link, snippet)
    """
    api_key = os.getenv("CUSTOM_SEARCH_API")
    cse_id = os.getenv("CSE_ID")

    if not api_key or not cse_id:
        raise ValueError("ENV ERROR")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id,
        "num": num,
    }
    response = requests.get(url, params=params)
    results = []
    if response.status_code == 200:
        data = response.json()
        for item in data.get("items", []):
            results.append({
                "title": item["title"],
                "link": item["link"],
                "snippet": item["snippet"],
            })
    else:
        print("Error:", response.status_code, response.text)
    return results


if __name__ == "__main__":
    # if api_key:
    #     print("CUSTOM_SEARCH_API is loaded.")
    # else:
    #     print("CUSTOM_SEARCH_API is not loaded.")

    # if cse_id:
    #     print("CSE_ID is loaded.")
    # else:
    #     print("CSE_ID is not loaded.")
        
    query = "python ppt generation"
    search_results = google_search(query)

    for i, result in enumerate(search_results, start=1):
        print(f"{i}. {result['title']}")
        print(result['link'])
        print(result['snippet'])
        print()