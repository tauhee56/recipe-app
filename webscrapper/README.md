# Lead Generation Web Scraper

A simple web scraping application that helps you gather company information from LinkedIn, similar to Apollo.io but for free use.

## Features

- Scrape company information from LinkedIn
- Get company details like:
  - Company website
  - Employee count
  - Industry
  - Location
- Simple web interface
- API endpoint for integration

## Installation

1. Install Python 3.8 or higher if you haven't already
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
python scraper.py
```

2. Open your web browser and go to: `http://localhost:5000`

3. Enter a company name and click "Scrape Company Data"

## Important Notes

- This is a basic version and should be used responsibly
- Respect website terms of service and robots.txt
- Add appropriate delays between requests
- Consider implementing:
  - Rate limiting
  - Proxy rotation
  - User authentication
  - Data storage
  - More detailed error handling

## Legal Disclaimer

This tool is for educational purposes only. Make sure to comply with the terms of service of any website you scrape and obtain necessary permissions.
