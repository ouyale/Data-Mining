# Kenya Job Boards Web Scraper 🇰🇪 &nbsp; [![View Code](https://img.shields.io/badge/Python-View_Script-orange?logo=python)](kenya_job_scraper.py)

![Python](https://img.shields.io/badge/Python-3.7+-blue?logo=python&logoColor=white)
![Firecrawl](https://img.shields.io/badge/Firecrawl-API-FF6B35)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-Output-000000?logo=json&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-success)

> **A Python web scraping tool that collects 5,000+ job listings from Kenyan job boards — extracting titles, companies, salaries, locations, and descriptions with intelligent retry logic and dual CSV/JSON export.**

<br>

<p align="center">
  <img src="https://img.shields.io/badge/📋_Jobs_Scraped-5,000+-green?style=for-the-badge" alt="Jobs"/>
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/🌐_Job_Boards-3_Sites-blue?style=for-the-badge" alt="Sites"/>
  &nbsp;&nbsp;
  <img src="https://img.shields.io/badge/📊_Output-CSV_+_JSON-orange?style=for-the-badge" alt="Output"/>
</p>

<br>

## Table of Contents

- [Problem Statement](#problem-statement)
- [Data Sources](#data-sources)
- [Architecture](#architecture)
- [Features](#features)
- [Output Schema](#output-schema)
- [Technologies Used](#technologies-used)
- [How to Run](#how-to-run)
- [Author](#author)

<br>

## Problem Statement

Kenya's job market data is scattered across multiple job boards with no unified API. This tool **automates the collection** of structured job data from three major Kenyan job platforms, enabling labor market analysis, salary benchmarking, and skills-demand research. The scraper handles JavaScript-heavy pages, anti-bot measures, and inconsistent salary formats across sites.

<br>

## Data Sources

| Job Board | URL | Specialization |
|-----------|-----|----------------|
| **BrighterMonday** | brightermonday.co.ke | Largest Kenyan job board |
| **Fuzu** | fuzu.com/job | Career development platform |
| **MyJobMag** | myjobmag.co.ke | Pan-African job listings |

<br>

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Job Board     │────▶│  Firecrawl   │────▶│  KenyanJob      │
│   URLs          │     │  API         │     │  Scraper         │
└─────────────────┘     └──────────────┘     │                  │
                                              │  • Site-specific │
                                              │    extraction    │
                                              │  • Salary parsing│
                                              │  • Retry logic   │
                                              └────────┬─────────┘
                                                       │
                                              ┌────────▼─────────┐
                                              │   Output         │
                                              │  • CSV file      │
                                              │  • JSON file     │
                                              │  • Log file      │
                                              └──────────────────┘
```

<br>

## Features

- **Multi-site scraping** — site-specific extraction methods for BrighterMonday, Fuzu, and MyJobMag with a generic fallback
- **Intelligent salary parsing** — handles ranges ("50,000 - 80,000"), K notation ("50K"), and normalizes to "KES X,XXX" format
- **Exponential backoff retry** — up to 3 retries per URL with increasing delays
- **Rate limiting** — 2-second delay between sites to avoid bans
- **Dual output** — CSV for analysis, JSON with metadata for archiving
- **OOP design** — clean `KenyanJobScraper` class with `JobListing` dataclass
- **Logging** — dual output to file (`job_scraper.log`) and console

```python
@dataclass
class JobListing:
    job_title: str
    company_name: str
    location: str
    date_posted: str
    minimum_salary: str
    maximum_salary: str
    job_description: str
    source_url: str
    scraped_at: str
```

<br>

## Output Schema

| Field | Type | Description |
|-------|------|-------------|
| `job_title` | string | Position title |
| `company_name` | string | Hiring company |
| `location` | string | City/region |
| `date_posted` | string | Posting date |
| `minimum_salary` | string | Salary floor (KES) |
| `maximum_salary` | string | Salary ceiling (KES) |
| `job_description` | string | Full job description text |
| `source_url` | string | Original listing URL |
| `scraped_at` | string | Timestamp of scrape |

<br>

## Technologies Used

| Tool | Purpose |
|------|---------|
| Python 3.7+ | Core language |
| Firecrawl API | Web scraping (handles JS-heavy sites) |
| Pandas | Data export & manipulation |
| python-dotenv | Environment variable management |
| Requests | HTTP connectivity |
| regex | Salary format parsing |
| dataclasses | Structured data objects |
| logging | Dual file/console logging |

<br>

## How to Run

```bash
# Clone the repository
git clone https://github.com/ouyale/Data-Mining.git
cd Data-Mining

# Install dependencies
pip install firecrawl-py python-dotenv pandas requests

# Set up your Firecrawl API key
cp env_template.sh .env
# Edit .env and add your FIRECRAWL_API_KEY

# Run the scraper
python kenya_job_scraper.py
```

Output files will be saved as CSV and JSON in the project directory.

<br>

## Author

**Barbara Obayi** — Machine Learning Engineer

[![GitHub](https://img.shields.io/badge/GitHub-ouyale-181717?logo=github)](https://github.com/ouyale)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Barbara_Obayi-0A66C2?logo=linkedin)](https://www.linkedin.com/in/barbara-weroba-obayi31/)
[![Portfolio](https://img.shields.io/badge/Portfolio-ouyale.github.io-4fc3f7)](https://ouyale.github.io)

---
