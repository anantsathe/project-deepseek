#!/usr/bin/env python3
"""
Discourse Scraper Runner Script

This script runs the Discourse scraper for TDS Jan 2025 course posts.
"""

from tds_scraper import scrape_discourse_posts
import argparse
import sys

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Scrape TDS Discourse posts')
    parser.add_argument('--output', '-o', default='discourse_posts_2025',
                       help='Output directory for scraped data')
    parser.add_argument('--url', '-u', default='https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34',
                       help='Base URL to scrape')
    args = parser.parse_args()

    # Configuration
    base_url = args.url
    output_dir = args.output

    print(f"Starting Discourse scraper for TDS Jan 2025 course...")
    print(f"Target URL: {base_url}")
    print(f"Output directory: {output_dir}")

    try:
        # Run the scraper
        total_scraped = scrape_discourse_posts(base_url, output_dir)
        if total_scraped == 0:
            print("\nWarning: No posts were scraped. Possible reasons:")
            print("- No posts in the specified date range (Jan 1 - Apr 14 2025)")
            print("- Website structure changed (check selectors in tds_scraper.py)")
            print("- Authentication required")
            print("- Website blocking scrapers")
        else:
            print(f"\nScraping complete! Total posts scraped: {total_scraped}")
        return 0 if total_scraped > 0 else 1
    except Exception as e:
        print(f"\nError during scraping: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    # Remove the direct function call that was outside main()
    sys.exit(main())