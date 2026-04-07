import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import re

# Directory to save papers
OUTPUT_DIR = "research_papers"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Queries mapping to the required domains
# Adding explicit terms related to the project where applicable.
# ArXiv is a highly reputable, global source of CS papers.
QUERIES = {
    "Psychology_UX": 'cat:cs.HC AND (all:psychology OR all:cognition OR all:"user experience")',
    "Backend_Scale": 'cat:cs.DC AND (all:scale OR all:load OR all:microservices OR all:"backend")',
    "Frontend_API": 'cat:cs.SE AND (all:"user interface" OR all:frontend OR all:API)',
    "LLM_Architecture": '(cat:cs.CL OR cat:cs.AI) AND (all:"large language model" OR all:LLM OR all:RAG)'
}

MAX_RESULTS_PER_QUERY = 25
BASE_URL = "http://export.arxiv.org/api/query?"

def clean_filename(title):
    # Remove invalid characters for Windows/Linux filenames
    clean = re.sub(r'[\\/:*?"<>|]', '_', title)
    # Remove newlines and extra spaces
    clean = ' '.join(clean.split())
    # Limit to ~100 chars to avoid extremely long paths
    return clean[:100].strip()

def search_and_download():
    all_papers_md = "# Downloaded Research Papers\n\nAll papers are downloaded from **ArXiv**, a globally trusted and reputable source for computer science research.\n\n"
    
    total_downloaded = 0
    
    for category, query in QUERIES.items():
        print(f"--- Fetching papers for category: {category} ---")
        all_papers_md += f"## {category}\n\n"
        
        # Create subfolder for this category
        category_dir = os.path.join(OUTPUT_DIR, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
        
        # URL encode query parameters
        params = urllib.parse.urlencode({
            'search_query': query,
            'start': 0,
            'max_results': MAX_RESULTS_PER_QUERY,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        })
        
        url = BASE_URL + params
        print(f"Querying URL: {url}")
        
        try:
            response = urllib.request.urlopen(url)
            xml_data = response.read()
        except Exception as e:
            print(f"Failed to fetch data for {category}: {e}")
            continue
            
        # Parse XML
        root = ET.fromstring(xml_data)
        
        # XML Namespace for Atom feed
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = root.findall('atom:entry', ns)
        if not entries:
            print(f"No results found for {category}.")
            continue
            
        for entry in entries:
            title = entry.find('atom:title', ns).text
            summary = entry.find('atom:summary', ns).text
            
            # Find PDF link
            pdf_url = None
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    pdf_url = link.get('href')
                    break
            
            # Fallback if specific pdf link title isn't present
            if not pdf_url:
                 for link in entry.findall('atom:link', ns):
                     if 'pdf' in link.get('href', ''):
                         pdf_url = link.get('href')
                         break
            
            if pdf_url:
                filename = f"{clean_filename(title)}.pdf"
                filepath = os.path.join(category_dir, filename)
                
                print(f"Downloading: {filename}")
                all_papers_md += f"### {clean_filename(title)}\n"
                all_papers_md += f"- **Path:** `{category}/{filename}`\n"
                all_papers_md += f"- **URL:** {pdf_url}\n"
                all_papers_md += f"- **Summary:** {' '.join(summary.split())[:300]}...\n\n"
                
                if not os.path.exists(filepath):
                    try:
                        # Add a small user-agent to avoid getting blocked
                        req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                            out_file.write(response.read())
                        total_downloaded += 1
                        time.sleep(3) # Be nice to arXiv API
                    except Exception as e:
                        print(f"Failed to download PDF from {pdf_url}: {e}")
                else:
                    print(f"File already exists: {filename}")
                    total_downloaded += 1
            else:
                print(f"No PDF link found for: {title}")
                
    # Write index file
    index_path = os.path.join(OUTPUT_DIR, "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(all_papers_md)
        
    print(f"\nDone! Downloaded/verified {total_downloaded} papers.")

if __name__ == "__main__":
    search_and_download()
