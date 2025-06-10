import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time
import json

def scrape_discourse_posts(base_url: str, output_dir: str):
    """Scrape TDS Discourse posts from 1 Jan 2025 - 14 Apr 2025"""
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 4, 14)
    
    os.makedirs(output_dir, exist_ok=True)
    
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
        
        # Find the topic list container - adjust this selector based on actual HTML
        topic_list = soup.find('div', class_='topic-list') or soup.find('table', {'class': 'topic-list'})
        
        if not topic_list:
            print("Could not find topic list container")
            return 0
            
        # Find individual topics - this selector may need adjustment
        topics = topic_list.find_all('tr', class_='topic-list-item') or topic_list.find_all('div', class_='topic-item')
        
        if not topics:
            print("No topics found in container")
            return 0
            
        scraped_count = 0
        
        for topic in topics:
            try:
                # Extract title and link
                title_link = topic.find('a', class_='title') or topic.find('a', class_='topic-title')
                if not title_link:
                    continue
                    
                topic_title = title_link.text.strip()
                topic_url = title_link['href']
                
                # Extract date - this is the tricky part that needs adjustment
                date_span = topic.find('span', class_='relative-date') or topic.find('span', class_='post-time')
                if not date_span:
                    continue
                    
                # Parse date - format might be different
                try:
                    post_date = datetime.strptime(date_span['title'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    # Try alternative date formats
                    date_text = date_span.text.strip()
                    if 'm' in date_text:  # e.g. "25m" for minutes
                        post_date = datetime.now()
                    elif 'h' in date_text:  # e.g. "2h" for hours
                        post_date = datetime.now()
                    else:
                        continue
                
                # Check date range
                if post_date < start_date or post_date > end_date:
                    continue
                
                # Scrape individual topic
                full_url = f"https://discourse.onlinedegree.iitm.ac.in{topic_url}"
                print(f"Scraping: {topic_title} ({post_date.date()})")
                
                topic_data = {
                    'title': topic_title,
                    'url': full_url,
                    'date': post_date.isoformat(),
                    'content': "",
                    'posts': []
                }
                
                # Scrape topic page
                topic_response = requests.get(full_url, headers=headers)
                if topic_response.status_code == 200:
                    topic_soup = BeautifulSoup(topic_response.text, 'html.parser')
                    
                    # Extract main content
                    main_post = topic_soup.find('div', class_='topic-post')
                    if main_post:
                        content = main_post.find('div', class_='post')
                        if content:
                            topic_data['content'] = content.get_text(' ', strip=True)
                    
                    # Save to file
                    filename = f"{post_date.strftime('%Y%m%d')}_{topic_title[:50]}.json"
                    filename = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in filename)
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(topic_data, f, ensure_ascii=False, indent=2)
                    
                    scraped_count += 1
                    time.sleep(1)  # Be polite
                
            except Exception as e:
                print(f"Error processing topic: {str(e)}")
                continue
                
        return scraped_count
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 0


def scrape_topic(topic_url: str) -> dict:
    """Scrape an individual topic and return structured data"""
    full_url = f"https://discourse.onlinedegree.iitm.ac.in{topic_url}"
    try:
        response = requests.get(full_url)
        if response.status_code != 200:
            print(f"Failed to fetch topic {topic_url}. Status code: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        topic_data = {
            'posts': []
        }
        
        # Extract topic metadata
        topic_container = soup.find('div', class_='topic-container')
        if topic_container:
            topic_data['title'] = topic_container.find('h1').text.strip() if topic_container.find('h1') else ""
            
        # Extract all posts in the topic
        posts = soup.find_all('div', class_='topic-post')
        for post in posts:
            post_data = {
                'author': post.get('data-username', ''),
                'post_number': post.get('data-post-number', ''),
                'content': "",
                'links': []
            }
            
            # Extract post content
            content = post.find('div', class_='post')
            if content:
                # Clean up content
                for element in content(['script', 'style', 'iframe', 'nav']):
                    element.decompose()
                
                post_data['content'] = content.get_text(' ', strip=True)
                
                # Extract all links
                for link in content.find_all('a', href=True):
                    post_data['links'].append({
                        'text': link.get_text(strip=True),
                        'url': link['href']
                    })
            
            topic_data['posts'].append(post_data)
        
        return topic_data
        
    except Exception as e:
        print(f"Error scraping topic {topic_url}: {str(e)}")
        return None

 


