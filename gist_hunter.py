import sys
import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
from dotenv import load_dotenv
import argparse

# Load environment variables from .env
load_dotenv()

CONFIG_FILE = ".workspace_config"

def get_db_file():
    """Retrieve the current workspace database file from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            db_file = f.read().strip() + ".db"
            if not os.path.exists(db_file):
                print("Workspace database not found. Please define a new workspace with '--define-workspace <name>'.")
                sys.exit(1)
            return db_file
    else:
        print("No workspace defined. Please use '--define-workspace <name>' to create one.")
        sys.exit(1)

def init_db(db_file):
    """Initialize the SQLite database."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def set_workspace(workspace_name):
    """Set a new workspace and initialize its database."""
    with open(CONFIG_FILE, "w") as f:
        f.write(workspace_name)
    print(f"Workspace '{workspace_name}' has been defined.")
    init_db(workspace_name + ".db")

def is_valid_gist(gist):
    """Check if the Gist has meaningful content in the metadata."""
    files = gist.get("files", {})
    for file_info in files.values():
        if file_info.get("size", 0) > 0:
            return True  # At least one file with content
    return False  # No meaningful content found

def fetch_gist_content(gist_url):
    """Fetch and validate the content of a Gist."""
    try:
        response = requests.get(gist_url, timeout=10)
        if response.status_code != 200:
            if verbose:
                print(f"Failed to fetch content from {gist_url}. Status Code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        files = soup.select(".file .highlight pre")

        # Suppress output if no content is found
        if not files:
            return None

        content = "\n".join(file.get_text() for file in files)
        return content if content.strip() else None  # Ensure content is not just whitespace

    except requests.Timeout:
        if verbose:
            print(f"Request to {gist_url} timed out.")
        return None

def save_to_db(gists, db_file):
    """Save discovered Gists to the database."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    for gist in gists:
        try:
            cursor.execute("INSERT INTO gists (url) VALUES (?)", (gist["html_url"],))
        except sqlite3.IntegrityError:
            pass  # Ignore duplicates
    conn.commit()
    conn.close()

def list_discovered_gists(db_file):
    """List all discovered Gists from the database."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, url FROM gists ORDER BY id")
        gists = cursor.fetchall()
    except sqlite3.OperationalError:
        print("No valid 'gists' table found. Please define a new workspace.")
        sys.exit(1)
    finally:
        conn.close()

    if gists:
        print("Discovered Gists:")
        for gist_id, url in gists:
            print(f"{gist_id} {url}")
    else:
        print("No discovered Gists found.")

def fetch_gist_by_id(gist_id, db_file):
    """Fetch a Gist from the database using its ID."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT url FROM gists WHERE id = ?", (gist_id,))
        row = cursor.fetchone()
    except sqlite3.OperationalError:
        print("No valid 'gists' table found. Please define a new workspace.")
        sys.exit(1)
    finally:
        conn.close()

    if row:
        url = row[0]
        print(f"Fetching Gist {url}...")
        content = fetch_gist_content(url)
        if content:
            print("\nGist Content:\n" + "-" * 40)
            print(content)
            print("-" * 40 + "\n")
        else:
            print("No content available for this Gist.")
    else:
        print(f"No Gist found with ID {gist_id}.")

def match_in_metadata(gist, search_terms):
    """Check if any search term matches the Gist metadata."""
    description = gist.get("description") or ""
    filenames = [file.get("filename", "") for file in gist.get("files", {}).values()]
    text_to_search = f"{description} {' '.join(filenames)}"

    for term in search_terms:
        if fuzz.partial_ratio(term, text_to_search) >= 50:
            return True
    return False

def scan_public_gists(search_terms, max_requests, verbose, db_file):
    """Scan through public Gists for potential matches."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"}
    url = "https://api.github.com/gists/public"
    matching_gists = []
    total_scanned = 0

    print("Scanning public Gists...")

    for _ in range(max_requests):
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            gists = response.json()
            total_scanned += len(gists)

            for gist in gists:
                if is_valid_gist(gist) and match_in_metadata(gist, search_terms):
                    content = fetch_gist_content(gist["html_url"])
                    if content:
                        matching_gists.append(gist)
                        if verbose:
                            print(f"Found matching Gist with content: {gist['html_url']}")

        url = response.links.get("next", {}).get("url")
        if not url:
            break

    print(f"Scanned {total_scanned} Gists.")
    print(f"Found {len(matching_gists)} matching Gists with valid content.")

    if matching_gists:
        print("Saving to workspace...")
        save_to_db(matching_gists, db_file)
    else:
        print("No matching Gists with valid content found.")

def main(search_terms, max_requests, verbose):
    """Main function to execute the Gist search."""
    db_file = get_db_file()
    print("Scanning public Gists...")
    scan_public_gists(search_terms, max_requests, verbose, db_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage and search public GitHub Gists with custom workspaces.")
    parser.add_argument("--define-workspace", help="Create a new workspace with the given name.")
    parser.add_argument("--list-discovered", action="store_true", help="List discovered Gists from the current workspace.")
    parser.add_argument("--fetch", type=int, help="Fetch the Gist by its ID from the current workspace.")
    parser.add_argument("--max-requests", type=int, default=10, help="Maximum number of requests (default: 10).")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("search_terms", nargs="*", help="Search terms to look for in Gists.")

    args = parser.parse_args()

    if args.define_workspace:
        set_workspace(args.define_workspace)
    elif args.list_discovered:
        db_file = get_db_file()
        list_discovered_gists(db_file)
    elif args.fetch is not None:
        db_file = get_db_file()
        fetch_gist_by_id(args.fetch, db_file)
    elif args.search_terms:
        main(args.search_terms, args.max_requests, args.verbose)
    else:
        print("No valid action provided. Use '--define-workspace' or '--list-discovered'.")
        sys.exit(1)
