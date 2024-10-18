# Gist Hunter

`Gist Hunter` is a powerful and efficient tool to search through public GitHub Gists using **fuzzy matching**. It helps you quickly find Gists containing specific terms in their metadata (e.g., description, filenames) or content. With incremental search capabilities, `Gist Hunter` avoids redundant searches by tracking already processed Gists.

## Features

- **Fuzzy Search:** Finds approximate matches for your search terms within Gists.
- **Metadata and Content Search:** Looks for terms in Gist descriptions, filenames, and content.
- **Incremental Search:** Uses a workspace log to skip previously processed Gists, saving time.
- **Rate Limit Handling:** Adapts to GitHub's API rate limits to prevent interruptions.
- **Custom Workspace Support:** Store logs in defined workspaces for different search contexts.

## Usage
```bash
python3 gist_hunter.py [search terms...] [output_file] [options]
```

## Example Usage:
``` bash
python3 gist_hunter.py "API key" "TODO" results.json --max-requests 20 --verbose
```
This will search for the terms "API key" and "TODO" across public Gists, saving the results to results.json.

## Options
`--max-requests`: Limit the number of Gists to search (default: 10).
`--verbose`: Enable detailed output of the search process.
`--workspace`: Define a custom workspace log path to track processed Gists.

## Using Custom Workspaces
``` bash
python3 gist_hunter.py --workspace=/path/to/workspace/company_name "API key" results.json
```
## Requirements
- Python 3.x
- Dependencies:
    - requests
    - beautifulsoup4
    - rapidfuzz
    - python-dotenv

To install the dependencies, run:
``` bash
pip install -r requirements.txt
```

## Setup

Clone the repository:
``` bash
git clone https://github.com/your-username/gist-hunter.git
cd gist-hunter
```

Create a .env file to store your GitHub token:
``` makefile
GITHUB_TOKEN=your_github_token_here
```

Run the script using the command line as shown above.

## How It Works

Search terms are applied to both Gist metadata and content.
Workspaces track which Gists have been processed to avoid redundant searches.
Pagination ensures all available Gists are searched, respecting API rate limits.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing
Feel free to submit issues or pull requests to improve the tool! Contributions are welcome.

# Enjoy hunting through Gists!