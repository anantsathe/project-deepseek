# discourse_api.py
import requests
import json
import os

def scrape_via_api():
    api_url = "https://discourse.onlinedegree.iitm.ac.in/posts.json"
    output_dir = "discourse_api_data"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            with open(os.path.join(output_dir, 'posts.json'), 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Saved API response to {output_dir}/posts.json")
            return True
        else:
            print(f"API request failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"API error: {str(e)}")
        return False