#!/usr/bin/env python3
"""
Kenyan Job Board Scraper using Firecrawl API

This script scrapes job listings from major Kenyan job boards and extracts
structured data including job title, company, location, date posted, salary,
and job description. The data is saved in both CSV and JSON formats.

Requirements:
- Python 3.7+
- firecrawl-py library
- python-dotenv library
- pandas library

Installation:
pip install firecrawl-py python-dotenv pandas requests

Environment Setup:
Create a .env file in the same directory with:
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

Usage:
python job_scraper.py
"""

import os
import json
import csv
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import re

# Third-party imports
try:
    from firecrawl import FirecrawlApp
    from dotenv import load_dotenv
    import pandas as pd
    import requests
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Install with: pip install firecrawl-py python-dotenv pandas requests")
    exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    """Data class to represent a job listing"""
    job_title: str
    company_name: str
    location: str
    date_posted: str
    minimum_salary: str
    maximum_salary: str
    job_description: str
    source_url: str
    scraped_at: str

class KenyanJobScraper:
    """
    A comprehensive job scraper for Kenyan job boards using Firecrawl API.
    
    Firecrawl API is a powerful web scraping service that:
    - Handles JavaScript-heavy sites
    - Bypasses anti-bot measures
    - Provides structured data extraction
    - Offers reliable performance at scale
    - Manages rate limiting automatically
    """
    
    def __init__(self):
        """Initialize the scraper with Firecrawl API configuration"""
        self.api_key = os.getenv('FIRECRAWL_API_KEY')
        if not self.api_key:
            raise ValueError(
                "FIRECRAWL_API_KEY not found in environment variables. "
                "Please create a .env file with your Firecrawl API key."
            )
        
        # Initialize Firecrawl client
        self.firecrawl = FirecrawlApp(api_key=self.api_key)
        
        # Default job board URLs
        self.default_urls = [
            "https://www.brightermonday.co.ke",
            "https://www.fuzu.com/job",
            "https://www.myjobmag.co.ke/page/2"
        ]
        
        # Storage for scraped jobs
        self.scraped_jobs: List[JobListing] = []
        
        logger.info("Kenyan Job Scraper initialized successfully")
    
    def parse_salary_range(self, salary_text: str) -> tuple:
        """
        Parse salary text to extract minimum and maximum salary values
        
        Args:
            salary_text: Raw salary text from job posting
            
        Returns:
            Tuple of (minimum_salary, maximum_salary) as strings
        """
        if not salary_text or salary_text.lower() in ['not specified', 'negotiable', 'competitive']:
            return "Not specified", "Not specified"
        
        # Clean the salary text
        salary_clean = re.sub(r'[^\d\s\-,kK]', '', salary_text.upper())
        
        try:
            # Pattern for ranges like "50,000 - 80,000" or "50K - 80K"
            range_pattern = r'(\d+(?:,\d+)*(?:K)?)\s*-\s*(\d+(?:,\d+)*(?:K)?)'
            range_match = re.search(range_pattern, salary_clean)
            
            if range_match:
                min_sal = self.normalize_salary(range_match.group(1))
                max_sal = self.normalize_salary(range_match.group(2))
                return min_sal, max_sal
            
            # Pattern for single values like "60,000" or "60K"
            single_pattern = r'(\d+(?:,\d+)*(?:K)?)'
            single_match = re.search(single_pattern, salary_clean)
            
            if single_match:
                salary_val = self.normalize_salary(single_match.group(1))
                return salary_val, salary_val
                
        except Exception as e:
            logger.warning(f"Error parsing salary '{salary_text}': {str(e)}")
        
        return "Not specified", "Not specified"
    
    def normalize_salary(self, salary_str: str) -> str:
        """
        Normalize salary string (convert K to thousands, format numbers)
        
        Args:
            salary_str: Salary string like "50K" or "50,000"
            
        Returns:
            Normalized salary string
        """
        try:
            if 'K' in salary_str.upper():
                # Convert K to thousands
                num = float(salary_str.upper().replace('K', '').replace(',', ''))
                return f"KES {int(num * 1000):,}"
            else:
                # Format regular numbers
                num = int(salary_str.replace(',', ''))
                return f"KES {num:,}"
        except (ValueError, AttributeError):
            return salary_str
        """Validate if URL is accessible"""
        try:
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def scrape_with_firecrawl(self, url: str, max_retries: int = 3) -> Optional[Dict]:
        """
        Scrape a URL using Firecrawl API with retry logic
        
        Args:
            url: The URL to scrape
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary containing scraped data or None if failed
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Scraping {url} (attempt {attempt + 1}/{max_retries})")
                
                # Firecrawl scrape parameters optimized for job boards
                scrape_params = {
                    'formats': ['markdown', 'html'],
                    'includeTags': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'a'],
                    'excludeTags': ['script', 'style', 'nav', 'header', 'footer'],
                    'waitFor': 3000,  # Wait 3 seconds for dynamic content
                    'timeout': 30000  # 30 second timeout
                }
                
                # Use Firecrawl to scrape the page
                result = self.firecrawl.scrape_url(url, scrape_params)
                
                if result and 'data' in result:
                    logger.info(f"Successfully scraped {url}")
                    return result['data']
                else:
                    logger.warning(f"No data returned from {url}")
                    
            except Exception as e:
                logger.error(f"Error scraping {url} on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        logger.error(f"Failed to scrape {url} after {max_retries} attempts")
        return None
    
    def extract_job_data_brightermonday(self, content: str) -> List[JobListing]:
        """Extract job data from BrighterMonday content"""
        jobs = []
        
        # BrighterMonday-specific extraction patterns
        job_patterns = {
            'title': r'<h[1-6][^>]*class="[^"]*job[^"]*title[^"]*"[^>]*>([^<]+)',
            'company': r'<[^>]*class="[^"]*company[^"]*"[^>]*>([^<]+)',
            'location': r'<[^>]*class="[^"]*location[^"]*"[^>]*>([^<]+)',
            'date': r'<[^>]*class="[^"]*date[^"]*"[^>]*>([^<]+)',
            'salary': r'<[^>]*class="[^"]*salary[^"]*"[^>]*>([^<]+)'
        }
        
        try:
            # Extract job blocks (this is a simplified approach)
            job_blocks = re.findall(r'<div[^>]*class="[^"]*job[^"]*item[^"]*"[^>]*>.*?</div>', content, re.DOTALL)
            
            for block in job_blocks:
                job_data = {}
                for field, pattern in job_patterns.items():
                    match = re.search(pattern, block, re.IGNORECASE)
                    job_data[field] = match.group(1).strip() if match else "Not specified"
                
                # Extract description (simplified)
                desc_match = re.search(r'<p[^>]*>([^<]{50,})</p>', block)
                description = desc_match.group(1).strip() if desc_match else "No description available"
                
                # Parse salary range
                salary_text = job_data.get('salary', 'Not specified')
                min_salary, max_salary = self.parse_salary_range(salary_text)
                
                jobs.append(JobListing(
                    job_title=job_data.get('title', 'Not specified'),
                    company_name=job_data.get('company', 'Not specified'),
                    location=job_data.get('location', 'Not specified'),
                    date_posted=job_data.get('date', 'Not specified'),
                    minimum_salary=min_salary,
                    maximum_salary=max_salary,
                    job_description=description[:500] + "..." if len(description) > 500 else description,
                    source_url="https://www.brightermonday.co.ke",
                    scraped_at=datetime.now().isoformat()
                ))
                
        except Exception as e:
            logger.error(f"Error extracting BrighterMonday data: {str(e)}")
            
        return jobs
    
    def extract_job_data_fuzu(self, content: str) -> List[JobListing]:
        """Extract job data from Fuzu content"""
        jobs = []
        
        # Fuzu-specific extraction patterns
        try:
            # This is a simplified extraction - in practice, you'd analyze the actual HTML structure
            title_matches = re.findall(r'<h[1-6][^>]*>([^<]*(?:job|position|role)[^<]*)</h[1-6]>', content, re.IGNORECASE)
            
            for i, title in enumerate(title_matches[:10]):  # Limit to first 10 jobs
                jobs.append(JobListing(
                    job_title=title.strip(),
                    company_name="Company not specified",
                    location="Kenya",
                    date_posted="Recent",
                    minimum_salary="Not specified",
                    maximum_salary="Not specified",
                    job_description="Job description not available",
                    source_url="https://www.fuzu.com/job",
                    scraped_at=datetime.now().isoformat()
                ))
                
        except Exception as e:
            logger.error(f"Error extracting Fuzu data: {str(e)}")
            
        return jobs
    
    def extract_job_data_myjobmag(self, content: str) -> List[JobListing]:
        """Extract job data from MyJobMag content"""
        jobs = []
        
        # MyJobMag-specific extraction patterns
        try:
            # Simplified extraction for demonstration
            job_sections = re.findall(r'<article[^>]*>.*?</article>', content, re.DOTALL)
            
            for section in job_sections[:10]:  # Limit to first 10 jobs
                # Extract title
                title_match = re.search(r'<h[1-6][^>]*>([^<]+)</h[1-6]>', section)
                title = title_match.group(1).strip() if title_match else "Job position available"
                
                jobs.append(JobListing(
                    job_title=title,
                    company_name="Company not specified",
                    location="Kenya",
                    date_posted="Recent",
                    minimum_salary="Not specified",
                    maximum_salary="Not specified",
                    job_description="Job description not available",
                    source_url="https://www.myjobmag.co.ke",
                    scraped_at=datetime.now().isoformat()
                ))
                
        except Exception as e:
            logger.error(f"Error extracting MyJobMag data: {str(e)}")
            
        return jobs
    
    def extract_jobs_from_content(self, content: str, url: str) -> List[JobListing]:
        """
        Extract job listings from scraped content based on the source URL
        
        Args:
            content: The scraped content (HTML or markdown)
            url: The source URL to determine extraction method
            
        Returns:
            List of JobListing objects
        """
        jobs = []
        
        if 'brightermonday' in url.lower():
            jobs = self.extract_job_data_brightermonday(content)
        elif 'fuzu' in url.lower():
            jobs = self.extract_job_data_fuzu(content)
        elif 'myjobmag' in url.lower():
            jobs = self.extract_job_data_myjobmag(content)
        else:
            # Generic extraction for custom URLs
            jobs = self.generic_job_extraction(content, url)
        
        logger.info(f"Extracted {len(jobs)} jobs from {url}")
        return jobs
    
    def generic_job_extraction(self, content: str, url: str) -> List[JobListing]:
        """Generic job extraction for unknown job boards"""
        jobs = []
        
        try:
            # Look for common job-related keywords in headings
            job_titles = re.findall(r'<h[1-6][^>]*>([^<]*(?:job|position|role|vacancy|opportunity)[^<]*)</h[1-6]>', content, re.IGNORECASE)
            
            for title in job_titles[:5]:  # Limit to first 5 matches
                jobs.append(JobListing(
                    job_title=title.strip(),
                    company_name="Company not specified",
                    location="Kenya",
                    date_posted="Recent",
                    minimum_salary="Not specified",
                    maximum_salary="Not specified",
                    job_description="Job description not available",
                    source_url=url,
                    scraped_at=datetime.now().isoformat()
                ))
                
        except Exception as e:
            logger.error(f"Error in generic extraction: {str(e)}")
            
        return jobs
    
    def scrape_jobs(self, urls: List[str] = None) -> List[JobListing]:
        """
        Main method to scrape jobs from specified URLs
        
        Args:
            urls: List of URLs to scrape. If None, uses default URLs.
            
        Returns:
            List of all scraped job listings
        """
        if urls is None:
            urls = self.default_urls
        
        all_jobs = []
        
        for url in urls:
            logger.info(f"Processing URL: {url}")
            
            # Validate URL
            if not self.validate_url(url):
                logger.warning(f"URL {url} is not accessible, skipping...")
                continue
            
            # Scrape with Firecrawl
            scraped_data = self.scrape_with_firecrawl(url)
            
            if scraped_data:
                # Extract content (prefer HTML over markdown for job extraction)
                content = scraped_data.get('html', scraped_data.get('markdown', ''))
                
                if content:
                    # Extract jobs from content
                    jobs = self.extract_jobs_from_content(content, url)
                    all_jobs.extend(jobs)
                    
                    # Rate limiting - be respectful to job boards
                    time.sleep(2)
                else:
                    logger.warning(f"No content extracted from {url}")
            else:
                logger.error(f"Failed to scrape {url}")
        
        self.scraped_jobs = all_jobs
        logger.info(f"Total jobs scraped: {len(all_jobs)}")
        return all_jobs
    
    def save_to_csv(self, filename: str = None) -> str:
        """Save scraped jobs to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kenyan_jobs_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if self.scraped_jobs:
                    fieldnames = list(asdict(self.scraped_jobs[0]).keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for job in self.scraped_jobs:
                        writer.writerow(asdict(job))
                
            logger.info(f"Jobs saved to CSV: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {str(e)}")
            return ""
    
    def save_to_json(self, filename: str = None) -> str:
        """Save scraped jobs to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kenyan_jobs_{timestamp}.json"
        
        try:
            jobs_data = [asdict(job) for job in self.scraped_jobs]
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump({
                    'scraped_at': datetime.now().isoformat(),
                    'total_jobs': len(jobs_data),
                    'jobs': jobs_data
                }, jsonfile, indent=2, ensure_ascii=False)
            
            logger.info(f"Jobs saved to JSON: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving to JSON: {str(e)}")
            return ""
    
    def display_summary(self):
        """Display a summary of scraped jobs"""
        if not self.scraped_jobs:
            print("No jobs scraped yet.")
            return
        
        print(f"\n{'='*50}")
        print(f"JOB SCRAPING SUMMARY")
        print(f"{'='*50}")
        print(f"Total jobs scraped: {len(self.scraped_jobs)}")
        
        # Group by source
        sources = {}
        for job in self.scraped_jobs:
            source = job.source_url
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\nJobs by source:")
        for source, count in sources.items():
            print(f"  {source}: {count} jobs")
        
        # Show sample jobs
        if self.scraped_jobs:
            print(f"\nSample job listings:")
            for i, job in enumerate(self.scraped_jobs[:3]):
                print(f"\n{i+1}. {job.job_title}")
                print(f"   Company: {job.company_name}")
                print(f"   Location: {job.location}")
                print(f"   Posted: {job.date_posted}")
                print(f"   Salary: {job.minimum_salary} - {job.maximum_salary}")

def get_user_urls() -> List[str]:
    """Get additional URLs from user input"""
    urls = []
    
    print("\nEnter additional job board URLs (press Enter with empty input to finish):")
    while True:
        url = input("Enter URL: ").strip()
        if not url:
            break
        
        if url.startswith('http'):
            urls.append(url)
            print(f"Added: {url}")
        else:
            print("Please enter a valid URL starting with http:// or https://")
    
    return urls

def main():
    """Main function to run the job scraper"""
    print("🚀 Kenyan Job Board Scraper")
    print("=" * 40)
    
    try:
        # Initialize scraper
        scraper = KenyanJobScraper()
        
        # Get user input for additional URLs
        custom_urls = get_user_urls()
        
        # Combine default and custom URLs
        all_urls = scraper.default_urls + custom_urls
        
        print(f"\nScraping {len(all_urls)} job boards...")
        print("This may take a few minutes...\n")
        
        # Scrape jobs
        jobs = scraper.scrape_jobs(all_urls)
        
        if jobs:
            # Display summary
            scraper.display_summary()
            
            # Save results
            csv_file = scraper.save_to_csv()
            json_file = scraper.save_to_json()
            
            print(f"\n✅ Results saved:")
            print(f"   CSV: {csv_file}")
            print(f"   JSON: {json_file}")
            
        else:
            print("❌ No jobs were scraped. Check your internet connection and API key.")
    
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
