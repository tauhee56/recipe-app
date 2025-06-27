import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import random

def scrape_leads(search_term, num_pages=2):
    try:
        leads = []
        
        # We'll use Google Jobs as an example (you can modify this for other business directories)
        base_url = f"https://www.google.com/search?q={search_term}+companies"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        for page in range(num_pages):
            try:
                # Add delay between requests to be respectful
                time.sleep(random.uniform(2, 4))
                
                url = f"{base_url}&start={page * 10}"
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find business listings
                for item in soup.find_all('div', class_='g'):
                    try:
                        title_elem = item.find('h3')
                        if not title_elem:
                            continue
                            
                        title = title_elem.text.strip()
                        description = item.find('div', class_='VwiC3b')
                        description = description.text.strip() if description else "N/A"
                        
                        website = item.find('cite')
                        website = website.text.strip() if website else "N/A"
                        
                        lead = {
                            'company_name': title,
                            'description': description,
                            'website': website,
                            'source': 'Google Search',
                            'date_found': datetime.now().strftime("%Y-%m-%d")
                        }
                        
                        leads.append(lead)
                        
                    except Exception as e:
                        print(f"Error processing item: {e}")
                        continue
                
                print(f"Processed page {page + 1}")
                
            except Exception as e:
                print(f"Error on page {page + 1}: {e}")
                continue
        
        # Save results to CSV
        if leads:
            filename = f'leads_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['company_name', 'description', 'website', 'source', 'date_found'])
                writer.writeheader()
                writer.writerows(leads)
            
            print(f"\nSuccessfully scraped {len(leads)} leads and saved to {filename}")
            
            # Print preview of leads
            print("\nPreview of leads found:")
            for i, lead in enumerate(leads[:5], 1):
                print(f"\n{i}. Company: {lead['company_name']}")
                print(f"   Website: {lead['website']}")
                print(f"   Description: {lead['description'][:100]}...")
                
        return True
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return False

if __name__ == "__main__":
    search_term = input("Enter industry or company type to search (e.g., 'software companies in karachi'): ")
    scrape_leads(search_term)
