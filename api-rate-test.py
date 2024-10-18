import os
import time
import requests
from rapidfuzz import fuzz, process
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def get_github_token():
    """Retrieve the GitHub token from the environment."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN not found. Make sure it is set in the .env file.")
        exit(1)
    return token

def check_rate_limit():
    """Check the current rate limit for the GitHub API."""
    token = get_github_token()
    headers = {"Authorization": f"token {token}"}
    
    try:
        response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors
        
        rate_limit_data = response.json()
        remaining = rate_limit_data['rate']['remaining']
        reset_time = rate_limit_data['rate']['reset']

        current_time = time.time()
        seconds_until_reset = reset_time - current_time

        print(f"Remaining Requests: {remaining}")
        print(f"Seconds Until Reset: {seconds_until_reset:.2f}")

    except requests.Timeout:
        print("Request to GitHub API timed out.")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

def fuzzy_search_in_rate_limit(data, search_term):
    """Perform fuzzy search on rate limit data."""
    lines = str(data).splitlines()
    matches = process.extract(search_term, lines, scorer=fuzz.partial_ratio)
    return [line for line, score, _ in matches if score >= 80]

if __name__ == "__main__":
    print("Checking GitHub API rate limit...")
    check_rate_limit()

    # Example of fuzzy searching the rate limit data (optional usage)
    search_term = input("Enter a term to search in the API response (or leave empty to skip): ")
    if search_term:
        token = get_github_token()
        headers = {"Authorization": f"token {token}"}
        response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
        rate_limit_data = response.json()
        results = fuzzy_search_in_rate_limit(rate_limit_data, search_term)

        if results:
            print("Fuzzy search results:")
            for result in results:
                print(result)
        else:
            print("No matches found.")
