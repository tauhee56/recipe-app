import requests
from bs4 import BeautifulSoup
import time
import json
import os
import logging
import re
from flask import Flask, request, jsonify, render_template
from urllib.parse import quote, urlparse
from fake_useragent import UserAgent
import cloudscraper
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class CompanyDataScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.scraper = cloudscraper.create_scraper(
            browser={'custom': self.ua.random},
            delay=2
        )
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def search_company(self, company_name):
        try:
            logger.info(f"Starting search for company: {company_name}")
            
            # Initialize company data
            company_data = {
                "name": company_name,
                "website": None,
                "description": None,
                "industry": None,
                "company_size": None,
                "revenue": None,
                "headquarters": None,
                "founded": None,
                "contacts": [],
                "social_profiles": {},
                "social_data": {
                    "linkedin": {},
                    "twitter": {},
                    "facebook": {},
                    "instagram": {}
                },
                "technologies": []
            }
            
            # Use multiple threads to gather data from different sources
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(self._search_google, company_name, company_data),
                    executor.submit(self._search_crunchbase, company_name, company_data),
                    executor.submit(self._search_bloomberg, company_name, company_data),
                    executor.submit(self._search_social_media, company_name, company_data),
                    executor.submit(self._search_linkedin_data, company_name, company_data)
                ]
                
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Error in data collection: {str(e)}")
            
            # If we found the website, get more info
            if company_data["website"]:
                self._get_website_info(company_data)
            
            # Clean and validate the data
            self._clean_company_data(company_data)
            
            logger.info(f"Extracted data: {company_data}")
            return company_data
            
        except Exception as e:
            logger.error(f"Error scraping {company_name}: {str(e)}")
            raise

    def _search_google(self, company_name, company_data):
        try:
            # First try Wikipedia for well-known companies
            search_url = f"https://www.google.com/search?q={quote(company_name)}+company+wikipedia"
            response = self.scraper.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Try to get data from Google's knowledge panel
            knowledge_panel = soup.select_one('.kp-header')
            if knowledge_panel:
                # Try to get description
                desc = knowledge_panel.select_one('.kno-rdesc span')
                if desc:
                    company_data["description"] = desc.text.strip()
                
                # Try to get other info
                for div in knowledge_panel.select('.rVusze'):
                    text = div.get_text().lower()
                    if 'founded:' in text:
                        company_data["founded"] = text.split('founded:')[1].strip()
                    elif 'headquarters:' in text:
                        company_data["headquarters"] = text.split('headquarters:')[1].strip()
                    elif 'revenue:' in text:
                        company_data["revenue"] = text.split('revenue:')[1].strip()
                    elif 'industry:' in text:
                        company_data["industry"] = text.split('industry:')[1].strip()
            
            # Search for company website and basic info
            search_url = f"https://www.google.com/search?q={quote(company_name)}+company+official+website"
            response = self.scraper.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Get website from search results
            for result in soup.select('.g')[:3]:
                link = result.select_one('a')
                if not link:
                    continue
                    
                url = link.get('href', '')
                if not url.startswith('http'):
                    continue
                
                domain = urlparse(url).netloc.lower()
                if any(s in domain for s in ['linkedin.com', 'facebook.com', 'twitter.com']):
                    company_data["social_profiles"][domain] = url
                    continue
                
                if not company_data["website"]:
                    company_data["website"] = url
            
            # Search for employees and size
            search_url = f"https://www.google.com/search?q={quote(company_name)}+company+employees+revenue+industry"
            response = self.scraper.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'lxml')
            
            text_content = soup.get_text().lower()
            
            # Look for employee count
            size_patterns = [
                r'(\d{1,3}(?:,\d{3})*(?:\+)?\s*employees)',
                r'((?:about|approximately|over|more than)\s+\d{1,3}(?:,\d{3})*\s+employees)',
                r'(team of \d{1,3}(?:,\d{3})*(?:\+)?)',
            ]
            
            for pattern in size_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    company_data["company_size"] = match.group(1)
                    break
            
            # Look for industry
            industry_patterns = [
                r'industry:\s*([^\.]+)',
                r'(?:is\s+)?(?:a|an)\s+([^,\.]+(?:company|corporation|manufacturer|producer|provider|retailer|supplier))',
                r'operates\s+in\s+the\s+([^,\.]+)\s+(?:industry|sector|market)',
                r'leading\s+([^,\.]+(?:company|manufacturer|producer|provider|retailer|supplier))',
            ]
            
            for pattern in industry_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    industry = match.group(1).strip()
                    if len(industry) > 5:  # Avoid very short matches
                        company_data["industry"] = industry
                        break
            
            # Look for revenue
            revenue_patterns = [
                r'revenue[:\s]+(?:US)?\$?\s*([\d\.]+\s*(?:billion|million|trillion))',
                r'(?:US)?\$?\s*([\d\.]+\s*(?:billion|million|trillion))\s+in\s+revenue',
            ]
            
            for pattern in revenue_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    company_data["revenue"] = f"${match.group(1)}"
                    break
                    
        except Exception as e:
            logger.warning(f"Error in Google search: {str(e)}")

    def _search_crunchbase(self, company_name, company_data):
        try:
            # Try different URL formats
            company_slugs = [
                company_name.lower().replace(' ', '-'),
                company_name.lower().replace(' ', ''),
                company_name.lower().replace(' ', '_'),
            ]
            
            for slug in company_slugs:
                try:
                    search_url = f"https://www.crunchbase.com/organization/{slug}"
                    response = self.scraper.get(search_url, headers=self.headers)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'lxml')
                        
                        # Try to get industry
                        industry_elem = soup.find('span', string=re.compile('Industries'))
                        if industry_elem and industry_elem.find_next('span'):
                            company_data["industry"] = industry_elem.find_next('span').text.strip()
                        
                        # Try to get company size
                        size_elem = soup.find('span', string=re.compile('Employee Count'))
                        if size_elem and size_elem.find_next('span'):
                            company_data["company_size"] = size_elem.find_next('span').text.strip()
                        
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error in Crunchbase search: {str(e)}")

    def _search_bloomberg(self, company_name, company_data):
        try:
            # Try different URL formats
            company_slugs = [
                company_name.lower().replace(' ', '-'),
                company_name.lower().replace(' ', ''),
                company_name.lower().replace(' ', '_'),
            ]
            
            for slug in company_slugs:
                try:
                    search_url = f"https://www.bloomberg.com/profile/{slug}"
                    response = self.scraper.get(search_url, headers=self.headers)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'lxml')
                        
                        # Try to get revenue
                        revenue_elem = soup.find('div', string=re.compile('Revenue'))
                        if revenue_elem and revenue_elem.find_next('div'):
                            company_data["revenue"] = revenue_elem.find_next('div').text.strip()
                        
                        # Try to get industry
                        industry_elem = soup.find('div', string=re.compile('Industry'))
                        if industry_elem and industry_elem.find_next('div'):
                            company_data["industry"] = industry_elem.find_next('div').text.strip()
                        
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error in Bloomberg search: {str(e)}")

    def _get_website_info(self, company_data):
        try:
            response = self.scraper.get(company_data["website"], headers=self.headers)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract technologies used
            self._extract_technologies(soup, company_data)
            
            # Look for contact information on various pages
            contact_pages = ['contact', 'about', 'team', 'leadership']
            base_url = company_data["website"].rstrip('/')
            
            for page in contact_pages:
                try:
                    page_url = f"{base_url}/{page}"
                    response = self.scraper.get(page_url, headers=self.headers)
                    if response.status_code == 200:
                        page_soup = BeautifulSoup(response.text, 'lxml')
                        self._extract_contacts(page_soup, company_data)
                except:
                    continue
            
            # Extract from main page as well
            self._extract_contacts(soup, company_data)
            
        except Exception as e:
            logger.warning(f"Error getting website info: {str(e)}")

    def _extract_contacts(self, soup, company_data):
        # Find email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        text_content = soup.get_text()
        
        # Find emails
        emails = re.findall(email_pattern, text_content)
        emails = [email for email in emails if not any(c.get('email') == email for c in company_data['contacts'])]
        
        # Find phone numbers
        phones = re.findall(phone_pattern, text_content)
        phones = [phone for phone in phones if not any(c.get('phone') == phone for c in company_data['contacts'])]
        
        # Look for contact names and titles
        name_patterns = [
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\s*[-–]\s*((?:CEO|CTO|CFO|Founder|Director|Manager|Head\s+of\s+[A-Za-z]+|VP\s+of\s+[A-Za-z]+))',
            r'((?:CEO|CTO|CFO|Founder|Director|Manager|Head\s+of\s+[A-Za-z]+|VP\s+of\s+[A-Za-z]+))\s*[-:]\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)',
        ]
        
        for pattern in name_patterns:
            matches = re.finditer(pattern, text_content)
            for match in matches:
                name, title = match.groups() if pattern.startswith('([A-Z]') else match.groups()[::-1]
                if not any(c.get('name') == name for c in company_data['contacts']):
                    company_data['contacts'].append({
                        'name': name.strip(),
                        'title': title.strip(),
                        'email': None,
                        'phone': None
                    })
        
        # Add standalone emails and phones
        for email in emails:
            company_data['contacts'].append({
                'name': None,
                'title': None,
                'email': email,
                'phone': None
            })
        
        for phone in phones:
            company_data['contacts'].append({
                'name': None,
                'title': None,
                'email': None,
                'phone': phone
            })

    def _extract_technologies(self, soup, company_data):
        tech_patterns = {
            'Frontend': [
                'React', 'Angular', 'Vue.js', 'Next.js', 'Nuxt.js',
                'jQuery', 'Bootstrap', 'Tailwind'
            ],
            'Backend': [
                'Node.js', 'Python', 'Java', 'PHP', 'Ruby', 'Go',
                'Django', 'Flask', 'Spring', 'Laravel'
            ],
            'Database': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
                'Oracle', 'SQL Server'
            ],
            'Cloud': [
                'AWS', 'Azure', 'Google Cloud', 'Heroku', 'DigitalOcean',
                'Cloudflare'
            ],
            'Analytics': [
                'Google Analytics', 'Mixpanel', 'Amplitude', 'Segment',
                'Hotjar'
            ]
        }
        
        found_tech = {category: [] for category in tech_patterns}
        page_source = str(soup).lower()
        
        for category, technologies in tech_patterns.items():
            for tech in technologies:
                if tech.lower() in page_source:
                    found_tech[category].append(tech)
        
        company_data['technologies'] = {k: v for k, v in found_tech.items() if v}

    def _clean_company_data(self, data):
        # Remove duplicate contacts
        if data['contacts']:
            unique_contacts = []
            seen = set()
            
            for contact in data['contacts']:
                key = json.dumps({k: v for k, v in contact.items() if v is not None}, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    unique_contacts.append(contact)
            
            data['contacts'] = unique_contacts
        
        # Clean up social profiles
        if data['social_profiles']:
            cleaned_profiles = {}
            for domain, url in data['social_profiles'].items():
                platform = next((name for name in ['linkedin', 'facebook', 'twitter'] if name in domain), domain)
                cleaned_profiles[platform] = url
            data['social_profiles'] = cleaned_profiles
        
        # Ensure all fields have at least None value
        required_fields = [
            'name', 'website', 'description', 'industry', 'company_size',
            'revenue', 'headquarters', 'founded', 'contacts', 'social_profiles',
            'social_data', 'technologies'
        ]
        
        for field in required_fields:
            if field not in data:
                data[field] = [] if field in ['contacts', 'technologies'] else None

    def _search_social_media(self, company_name, company_data):
        try:
            # Search for social media profiles
            platforms = {
                'facebook': 'facebook.com',
                'twitter': 'twitter.com',
                'instagram': 'instagram.com',
            }
            
            for platform, domain in platforms.items():
                try:
                    search_url = f"https://www.google.com/search?q=site:{domain}+{quote(company_name)}+official"
                    response = self.scraper.get(search_url, headers=self.headers)
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    for result in soup.select('.g')[:2]:  # Look at top 2 results
                        link = result.select_one('a')
                        if not link:
                            continue
                            
                        url = link.get('href', '')
                        if not url.startswith('http'):
                            continue
                            
                        # Get social media stats if available
                        desc = result.select_one('.VwiC3b')
                        if desc:
                            text = desc.text.lower()
                            followers = None
                            
                            # Try to extract follower count
                            follower_patterns = [
                                r'([\d,.]+\s*(?:k|m|b)?)\s*(?:followers|fans|likes)',
                                r'(?:followed by|following)\s*([\d,.]+\s*(?:k|m|b)?)',
                            ]
                            
                            for pattern in follower_patterns:
                                match = re.search(pattern, text, re.IGNORECASE)
                                if match:
                                    followers = match.group(1)
                                    break
                            
                            company_data["social_data"][platform] = {
                                "url": url,
                                "followers": followers,
                                "description": text
                            }
                            
                            company_data["social_profiles"][platform] = url
                        break
                        
                except Exception as e:
                    logger.warning(f"Error searching {platform}: {str(e)}")
                    
        except Exception as e:
            logger.warning(f"Error in social media search: {str(e)}")

    def _search_linkedin_data(self, company_name, company_data):
        try:
            # Search for LinkedIn company page
            search_url = f"https://www.google.com/search?q=site:linkedin.com/company/+{quote(company_name)}+about"
            response = self.scraper.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'lxml')
            
            linkedin_data = {}
            
            for result in soup.select('.g')[:2]:
                link = result.select_one('a')
                desc = result.select_one('.VwiC3b')
                
                if not link or not desc:
                    continue
                    
                url = link.get('href', '')
                if not url.startswith('http') or 'linkedin.com/company/' not in url:
                    continue
                
                text = desc.text.lower()
                
                # Try to extract employee count
                employee_patterns = [
                    r'([\d,]+(?:\+)?)\s*employees',
                    r'([\d,.]+k?\+?)\s*employees',
                ]
                
                for pattern in employee_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        linkedin_data["employees"] = match.group(1)
                        break
                
                # Try to extract location
                location_patterns = [
                    r'(?:headquarters|located in|based in)\s*([^\.]+)',
                    r'(?:from|in)\s*((?:[A-Z][a-z]+(?:\s*,\s*)?)+)',
                ]
                
                for pattern in location_patterns:
                    match = re.search(pattern, text)
                    if match:
                        linkedin_data["location"] = match.group(1).strip()
                        break
                
                # Try to extract specialties
                specialty_patterns = [
                    r'specialties?:?\s*([^\.]+)',
                    r'specializing in\s*([^\.]+)',
                ]
                
                for pattern in specialty_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        linkedin_data["specialties"] = [
                            s.strip() for s in match.group(1).split(',')
                        ]
                        break
                
                # Try to get company type
                type_patterns = [
                    r'(?:is\s+)?(?:a|an)\s+([^,\.]+(?:company|corporation|manufacturer|producer|provider))',
                    r'type:?\s*([^\.]+)',
                ]
                
                for pattern in type_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        linkedin_data["company_type"] = match.group(1).strip()
                        break
                
                company_data["social_data"]["linkedin"] = linkedin_data
                company_data["social_profiles"]["linkedin"] = url
                break
                
        except Exception as e:
            logger.warning(f"Error in LinkedIn data search: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.json
        company_name = data.get('company_name')
        filters = data.get('filters', {})
        scraper = CompanyDataScraper()
        
        # If company name is provided, search directly
        if company_name:
            result = scraper.search_company(company_name)
            if result:
                return jsonify(result)
            return jsonify({"error": "Company not found"}), 404
            
        # Otherwise, use filters
        search_terms = []
        
        if filters.get('industry'):
            search_terms.append(f"{filters['industry']} companies")
            
        if filters.get('location'):
            search_terms.append(f"in {filters['location']}")
            
        if filters.get('size'):
            size_map = {
                '1-10': 'small',
                '11-50': 'small to medium',
                '51-200': 'medium',
                '201-500': 'medium to large',
                '501-1000': 'large',
                '1001+': 'enterprise'
            }
            if filters['size'] in size_map:
                search_terms.append(f"{size_map[filters['size']]} companies")
            
        if filters.get('keywords'):
            search_terms.extend(filters['keywords'].split(','))
        
        # If no search criteria, return error
        if not search_terms:
            return jsonify({'error': 'Please enter a company name or set search filters'}), 400
        
        # Search for companies
        companies = []
        search_query = ' '.join(search_terms)
        search_url = f"https://www.google.com/search?q={quote(search_query)}+companies"
        response = scraper.scraper.get(search_url, headers=scraper.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract company names from search results
        for result in soup.select('.g')[:5]:  # Get top 5 results
            title = result.select_one('h3')
            if not title:
                continue
                
            company_name = title.text.strip()
            # Skip if it's not a company name
            if any(x in company_name.lower() for x in ['list of', 'top 10', 'best']):
                continue
                
            # Clean company name
            company_name = re.sub(r'\s*\|.*$', '', company_name)  # Remove text after |
            company_name = re.sub(r'\s*-.*$', '', company_name)   # Remove text after -
            company_name = re.sub(r'(?i)\s*inc\.?$', '', company_name)  # Remove Inc
            company_name = re.sub(r'(?i)\s*llc\.?$', '', company_name)  # Remove LLC
            company_name = company_name.strip()
            
            # Get company data
            company_data = scraper.search_company(company_name)
            if company_data:
                companies.append(company_data)
        
        if not companies:
            return jsonify([])  # Return empty list if no matches
            
        return jsonify(companies)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
