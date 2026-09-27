from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
import os
from bs4 import BeautifulSoup
from crawler.spider import AsyncSpider
from indexer.ranker import SearchEngineIndex

# Initialize our FastAPI app
app = FastAPI(title="Semantic Vector Search API")

# Initialize our global classes (No more TextProcessor!)
search_index = SearchEngineIndex()

# Global state flags
is_crawling = False
is_indexed = False

@app.get("/")
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serves the frontend HTML UI."""
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'index.html')
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    return HTMLResponse(content=html_content, status_code=200)

async def run_crawler_and_indexer():
    """Background task that runs the spider and indexes the data."""
    global is_crawling, is_indexed
    is_crawling = True
    
    # 1. Start the crawler
    print("\n--- STARTING THE CRAWLER ---")
    spider = AsyncSpider()
    crawled_data = await spider.crawl()
    
    # 2. Process and Index the crawled HTML
    print(f"\n--- CRAWLING FINISHED. INDEXING {len(crawled_data)} PAGES ---")
    for page in crawled_data:
        url = page['url']
        html = page['html']
        
        # Extract plain text from HTML (the AI model needs raw sentences, not code tags)
        soup = BeautifulSoup(html, "html.parser")
        raw_text = soup.get_text(separator=" ", strip=True)
        
        # Add the text directly to the FAISS Vector Index
        search_index.add_document(url, raw_text)
        
    is_crawling = False
    is_indexed = True
    print(f"\n--- INDEXING COMPLETE! Total documents: {search_index.doc_counter} ---")

@app.post("/crawl")
async def start_crawl(background_tasks: BackgroundTasks):
    """Endpoint to manually trigger the crawler without freezing the API."""
    global is_crawling
    if is_crawling:
        return {"message": "Crawler is already running! Please wait."}
    
    # Add the heavy crawling job to a background task so the API responds instantly
    background_tasks.add_task(run_crawler_and_indexer)
    return {"message": "Crawling and indexing started in the background. Check your terminal for progress!"}

@app.get("/search")
async def search(q: str):
    """Endpoint to search the indexed semantic data."""
    if not is_indexed:
        return {"message": "Please run the /crawl endpoint first to build the index."}
        
    # Search the FAISS vector index directly using the raw query string
    results = search_index.search(q)
    
    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }