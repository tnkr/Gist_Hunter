import sys
import os
import time
import requests
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz
from dotenv import load_dotenv
import itertools
import threading
import argparse

# Load environment variables from .env
load_dotenv()

CONFIG_FILE = ".workspace_config"

def get_github_token():
    """Retrieve the GitHub token from the environment."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN not found. Make sure it is set in the .env file.")
        exit(1)
    return token

def load_workspace():
    """Load the saved workspace path from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return f.read().strip()
    return "workspace.log"

def save_workspace(workspace):
    """Save the new workspace path to the config file."""
    with open(CONFIG_FILE, "w") as f:
        f.write(workspace)

def read_workspace_log(log_file):
    """Read the workspace log and return a set of processed Gist IDs."""
    if not os.path.exists(log_file):
        return set()
    with open(log_file, "r") as f:
        return set(line.strip() for line in f)

def update_workspace_log(log_file, gist_id):
    """Append a Gist ID to the workspace log."""
    with open(log_file, "a") as f:
        f.write(gist_id + "\n")

def check_rate_limit():
    """Check the current rate limit for the GitHub API."""
    token = get_github_token()
    headers = {"Authorization": f"token {token}"}
    response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)

    if response.status_code == 200:
        rate_limit_data = response.json()
        remaining = rate_limit_data['rate']['remaining']
        reset_time = rate_limit_data['rate']['reset']

        current_time = time.time()
        seconds_until_reset = reset_time - current_time

        print(f"Remaining Requests: {remaining}")
        print(f"Seconds Until Reset: {seconds_until_reset:.2f}")

        return remaining, seconds_until_reset
    else:
        print(f"Failed to fetch rate limit. Status Code: {response.status_code}")
        print(response.json())
        exit(1)

def match_in_metadata(gist, search_terms):
    """Check if any search term matches the Gist metadata."""
    description = gist.get("description") or ""
    filenames = [file.get("filename", "") for file in gist.get("files", {}).values()]
    text_to_search = f"{description} {' '.join(filenames)}"

    for term in search_terms:
        if fuzz.partial_ratio(term, text_to_search) >= 50:
            return True
    return False

def fetch_matching_gists(search_terms, max_requests, verbose, log_file):
    """Fetch only matching Gists based on metadata."""
    token = get_github_token()
    headers = {"Authorization": f"token {token}"}
    url = "https://api.github.com/gists/public"
    all_results = {}
    processed_gists = read_workspace_log(log_file)

    for _ in range(max_requests):
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            gists = response.json()

            for gist in gists:
                gist_id = gist["id"]
                if gist_id in processed_gists:
                    if verbose:
                        print(f"Skipping already processed Gist: {gist_id}")
                    continue

                if match_in_metadata(gist, search_terms):
                    gist_url = gist["html_url"]
                    if verbose:
                        print(f"Fetching matching Gist: {gist_url}")

                    content = get_gist_content(gist_url, verbose)
                    matches = fuzzy_search_in_content(content, search_terms)

                    if matches:
                        all_results[gist_url] = matches

                # Update the log with the processed Gist ID
                update_workspace_log(log_file, gist_id)

        url = response.links.get("next", {}).get("url")
        if not url:
            break

    return all_results

def get_gist_content(gist_url, verbose):
    """Fetch and scrape the content of a matching Gist."""
    try:
        response = requests.get(gist_url, timeout=10)
        if response.status_code != 200:
            if verbose:
                print(f"Failed to fetch content from {gist_url}. Status Code: {response.status_code}")
            return ""
    except requests.Timeout:
        print(f"Request to {gist_url} timed out.")
        return ""

    soup = BeautifulSoup(response.content, "html.parser")
    files = soup.select(".file .highlight pre")
    return "\n".join(file.get_text() for file in files)

def fuzzy_search_in_content(content, search_terms):
    """Perform fuzzy search for multiple terms."""
    lines = content.splitlines()
    results = {}
    for term in search_terms:
        matches = process.extract(term, lines, scorer=fuzz.partial_ratio, score_cutoff=50)
        if matches:
            results[term] = [line for line, score, _ in matches]
    return results

def spinner():
    """Display a spinning animation while the script runs."""
    for frame in itertools.cycle(['|', '/', '-', '\\']):
        print(f"\rRunning... {frame}", end='', flush=True)
        time.sleep(0.1)

def calculate_safe_interval(remaining, seconds_until_reset):
    """Calculate the minimum interval between requests to stay within the rate limit."""
    if remaining == 0:
        print("No remaining requests available. Please wait for the reset period.")
        exit(1)

    # Calculate the interval to evenly distribute requests
    interval = seconds_until_reset / remaining
    return max(interval, 1)  # Ensure the interval is at least 1 second

def search_gists(search_terms, output_file, max_requests, verbose, log_file):
    """Search Gists based on metadata and fetch matching ones."""
    remaining, seconds_until_reset = check_rate_limit()
    if max_requests > remaining:
        print(f"Error: The script requires {max_requests} requests, but only {remaining} are available.")
        exit(1)

    interval = calculate_safe_interval(remaining, seconds_until_reset)
    total_time = max_requests * interval
    print(f"Estimated time to complete: {total_time:.2f} seconds")

    if not verbose:
        spinner_thread = threading.Thread(target=spinner, daemon=True)
        spinner_thread.start()

    all_results = fetch_matching_gists(search_terms, max_requests, verbose, log_file)

    print("\nSearch complete. Saving results...")
    if all_results:
        with open(output_file, "w") as f:
            f.write(str(all_results))
        print(f"Results saved to {output_file}")
    else:
        print("No matches found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search public GitHub Gists using metadata and fuzzy matching.")
    parser.add_argument("search_terms", nargs="+", help="Search terms to look for in Gists.")
    parser.add_argument("output_file", help="Output file to save the results.")
    parser.add_argument("--max-requests", type=int, default=10, help="Maximum number of Gists to search (default: 10).")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--workspace", help="Set or override the workspace log file path.")

    args = parser.parse_args()

    workspace = args.workspace or load_workspace()
    if args.workspace:
        save_workspace(args.workspace)

    search_terms = args.search_terms[:-1]
    output_file = args.search_terms[-1]
    max_requests = args.max_requests
    verbose = args.verbose

    search_gists(search_terms, output_file, max_requests, verbose, workspace)
