from flask import Flask, render_template, request, jsonify
import requests
import time
import random

app = Flask(__name__)

# Sample company database
COMPANIES_DB = {
    "technology": [
        {
            "name": "Google",
            "description": "Search engine and technology company",
            "industry": "Technology",
            "website": "google.com",
            "location": "Mountain View, California"
        },
        {
            "name": "Microsoft",
            "description": "Software and cloud computing company",
            "industry": "Technology",
            "website": "microsoft.com",
            "location": "Redmond, Washington"
        },
        {
            "name": "Apple",
            "description": "Consumer electronics and software company",
            "industry": "Technology",
            "website": "apple.com",
            "location": "Cupertino, California"
        }
    ],
    "automotive": [
        {
            "name": "Tesla",
            "description": "Electric vehicle and clean energy company",
            "industry": "Automotive",
            "website": "tesla.com",
            "location": "Austin, Texas"
        },
        {
            "name": "Ford",
            "description": "Automobile manufacturer",
            "industry": "Automotive",
            "website": "ford.com",
            "location": "Dearborn, Michigan"
        }
    ],
    "retail": [
        {
            "name": "Amazon",
            "description": "E-commerce and technology company",
            "industry": "Retail",
            "website": "amazon.com",
            "location": "Seattle, Washington"
        },
        {
            "name": "Walmart",
            "description": "Retail corporation",
            "industry": "Retail",
            "website": "walmart.com",
            "location": "Bentonville, Arkansas"
        }
    ],
    "finance": [
        {
            "name": "JPMorgan Chase",
            "description": "Banking and financial services",
            "industry": "Finance",
            "website": "jpmorganchase.com",
            "location": "New York City, New York"
        },
        {
            "name": "Goldman Sachs",
            "description": "Investment banking and securities",
            "industry": "Finance",
            "website": "goldmansachs.com",
            "location": "New York City, New York"
        }
    ],
    "healthcare": [
        {
            "name": "Johnson & Johnson",
            "description": "Healthcare and pharmaceutical company",
            "industry": "Healthcare",
            "website": "jnj.com",
            "location": "New Brunswick, New Jersey"
        },
        {
            "name": "UnitedHealth Group",
            "description": "Healthcare and insurance company",
            "industry": "Healthcare",
            "website": "unitedhealthgroup.com",
            "location": "Minnetonka, Minnesota"
        }
    ]
}

def search_companies(query):
    query = query.lower()
    results = []
    
    # Search through all categories
    for category, companies in COMPANIES_DB.items():
        if query in category.lower():
            # If query matches category, add all companies in that category
            results.extend(companies)
        else:
            # Search individual companies
            for company in companies:
                if (query in company['name'].lower() or 
                    query in company['description'].lower() or
                    query in company['industry'].lower() or
                    query in company['location'].lower()):
                    results.append(company)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for company in results:
        company_key = company['name']
        if company_key not in seen:
            seen.add(company_key)
            unique_results.append(company)
    
    return unique_results[:10]  # Limit to 10 results

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([])
    
    # Add a small delay to simulate API call
    time.sleep(random.uniform(0.1, 0.5))
    
    companies = search_companies(query)
    return jsonify(companies)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
