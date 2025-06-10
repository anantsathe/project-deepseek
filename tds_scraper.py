# tds_scraper.py
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time
import json
import re

def scrape_discourse_posts(base_url: str, output_dir: str):
    """Scrape TDS Discourse posts with updated selectors"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Scraping {base_url}")
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return 0
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Save the HTML for inspection
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, 'debug_page.html'), 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # New approach to find topics - looking for topic rows
        topics = []
        for row in soup.find_all('tr'):
            if 'data-topic-id' in row.attrs:
                topics.append(row)
        
        if not topics:
            print("Alternative approach: Looking for topic links")
            topics = soup.select('a.title, a.topic-title')
        
        if not topics:
            print("Could not find any topics using any method")
            return 0
            
        print(f"Found {len(topics)} potential topics")
        scraped_count = 0
        
        for topic in topics[:5]:  # Limit to 5 for testing
            try:
                # Extract topic info
                if topic.name == 'tr':
                    # Handle table row format
                    title_link = topic.find('a', class_='title') or topic.find('a', class_='topic-title')
                    date_span = topic.find('span', class_='relative-date') or topic.find('span', class_='post-time')
                else:
                    # Handle direct link format
                    title_link = topic
                    date_span = topic.find_next('span', class_='relative-date')
                
                if not title_link or not hasattr(title_link, 'href'):
                    continue
                    
                topic_title = title_link.text.strip()
                topic_url = title_link['href']
                
                # Handle relative URLs
                if not topic_url.startswith('http'):
                    topic_url = f"https://discourse.onlinedegree.iitm.ac.in{topic_url}"
                
                # Extract date - handle multiple formats
                post_date = None
                if date_span and hasattr(date_span, 'attrs') and 'title' in date_span.attrs:
                    try:
                        post_date = datetime.strptime(date_span['title'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    except ValueError:
                        pass
                
                if not post_date:
                    print(f"Could not parse date for {topic_title}, using current date")
                    post_date = datetime.now()
                
                # Save topic data
                filename = re.sub(r'[^\w\-_]', '_', topic_title)[:50] + '.json'
                filepath = os.path.join(output_dir, filename)
                
                topic_data = {
                    'title': topic_title,
                    'url': topic_url,
                    'date': post_date.isoformat(),
                    'scraped_at': datetime.now().isoformat()
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(topic_data, f, indent=2)
                
                scraped_count += 1
                print(f"Saved: {filename}")
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing topic: {str(e)}")
                continue
                
        return scraped_count
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 0