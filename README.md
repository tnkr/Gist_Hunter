# Gist Hunter

## This is a massive work-in-progress ## 

`Gist Hunter` is a tool to search through public GitHub Gists using **fuzzy matching**. It helps you quickly find Gists containing specific terms in their metadata (e.g., description, filenames) or content. With incremental search capabilities, `Gist Hunter` avoids redundant searches by tracking already processed Gists.


## Important - **you will need a Github API token** ##


## Requirements
- Python 3.x
- Dependencies:
    - requests
    - beautifulsoup4
    - rapidfuzz
    - python-dotenv

```bash
> python3 gist_hunter.py --help
usage: gist_hunter.py [-h] [--define-workspace DEFINE_WORKSPACE] [--list-discovered] [--fetch FETCH]
                      [--max-requests MAX_REQUESTS] [--verbose]
                      [search_terms ...]

Manage and search public GitHub Gists with custom workspaces.

positional arguments:
  search_terms          Search terms to look for in Gists.

options:
  -h, --help            show this help message and exit
  --define-workspace DEFINE_WORKSPACE
                        Create a new workspace with the given name.
  --list-discovered     List discovered Gists from the current workspace.
  --fetch FETCH         Fetch the Gist by its ID from the current workspace.
  --max-requests MAX_REQUESTS
                        Maximum number of requests (default: 10).
  --verbose             Enable verbose output.
```


## Setup

Clone the repository:
``` bash
git clone https://github.com/your-username/gist-hunter.git
cd gist-hunter
```
***recommend using virtualenv to create a virtual environment***

**Create a .env file to store your GitHub token:**
``` makefile
GITHUB_TOKEN=your_github_token_here
```

## How It Works

`Gist Hunter` allows you to search through public GitHub Gists for specific keywords, save the matching results into a custom workspace, and fetch their content when needed. Below is an overview of the key features and workflow.

### 1. Defining a Workspace
Before starting a scan, you need to define a workspace where the results will be saved. The workspace is tied to a database that stores the discovered Gists.

### 2. Searching for Gists
You can search for public Gists using keywords. The scan will look through the Gist metadata (filenames and descriptions) to find matches.

### 3. Avoiding Noisy Results
Gists with no meaningful content are ignored and not saved to the workspace.
Errors such as request timeouts or failed content retrieval will only be shown if `--verbose` mode is enabled.

### Example Workflow:

```bash
python3 gist_hunter.py --define-workspace USER_SUPPLIED_NAME
```

```bash
python3 gist_hunter.py "API key" "TODO" --max-requests (number of requests)
```

```bash
python3 gist_hunter.py --list-discovered
```
**Example output:**
```
Discovered Gists:
1 https://gist.github.com/user1/abc123
2 https://gist.github.com/user2/def456
```

```bash
python3 gist_hunter.py --fetch (#)
```

**Example output**

```
Fetching Gist https://gist.github.com/user1/abc123...


Gist Content:
----------------------------------------
# Example Python Code
import requests

print("Hello, world!")
----------------------------------------
```

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing
Feel free to submit issues or pull requests to improve the tool! Contributions are welcome.

# Enjoy hunting through Gists!
