from setuptools import setup, find_packages

# Read the contents of README for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gist-hunter",
    version="0.1.0",
    author="tnkr",
    author_email="tnkrsec@outlook.com",
    description="A tool to search public GitHub Gists with fuzzy matching and rate-limit handling.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/your-repo",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4==4.12.2",
        "rapidfuzz==3.10.0",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "gist_search=gist_search:main",  # Expose the script as a CLI tool
        ],
    },
)
