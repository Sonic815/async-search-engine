# crawler/spider.py
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import time

# Set up basic logging so we can see what the crawler is doing
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from utils.config import SEED_URLS, MAX_CONCURRENT_REQUESTS, MAX_PAGES_TO_CRAWL, HEADERS

class AsyncSpider:
    def __init__(self):
        # A queue to hold the URLs we need to visit
        self.queue = asyncio.Queue()
        # A set to track URLs we've already seen (prevents infinite loops)
        self.visited = set()
        # A list to store the raw HTML of the pages we successfully crawl
        self.crawled_data = []

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> str:
        """Asynchronously downloads HTML, verifying content type first."""
        try:
            # We use a timeout to ensure a broken website doesn't freeze our crawler
            async with session.get(url, headers=HEADERS, timeout=10) as response:
                
                # Check 1: Did the server return a success code?
                if response.status != 200:
                    logging.warning(f"Failed to fetch {url} (Status: {response.status})")
                    return ""
                    
                # Check 2: Is this actually a text/HTML webpage? 
                # (Prevents downloading gigabytes of PDFs or MP4s)
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    logging.info(f"Skipping non-HTML file: {url}")
                    return ""

                # If it passed the checks, download the text
                return await response.text()
                
        except asyncio.TimeoutError:
            logging.warning(f"Timeout while fetching {url}")
            return ""
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return ""

    def extract_links(self, html: str, base_url: str) -> list:
        """Parses HTML to find all hyperlinks and converts relative URLs to absolute."""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            # Ignore anchor links or javascript links
            if href.startswith(("#", "javascript:")):
                continue
                
            # Convert relative links (like /wiki/Data) to full URLs
            full_url = urljoin(base_url, href)
            
           # Restrict crawling to standard HTTP/HTTPS links
            # (Ignores 'mailto:', 'ftp:', or base64 image strings)
            if full_url.startswith(("http://", "https://")):
                links.append(full_url)
                
        return links

    async def worker(self, name: str, session: aiohttp.ClientSession):
        """A worker task that constantly pulls URLs from the queue and processes them."""
        while len(self.visited) < MAX_PAGES_TO_CRAWL:
            try:
                # Wait for a URL to appear in the queue
                url = await self.queue.get()
                
                if url in self.visited:
                    self.queue.task_done()
                    continue

                logging.info(f"[{name}] Crawling: {url}")
                self.visited.add(url)
                await asyncio.sleep(1)
                # 1. Fetch the HTML
                html = await self.fetch(session, url)
                
                if html:
                    # Save the data for the next step of our project (Indexing)
                    self.crawled_data.append({"url": url, "html": html})
                    
                    # 2. Extract new links
                    new_links = self.extract_links(html, url)
                    
                    # 3. Add new links to the queue if we haven't visited them
                    for link in new_links:
                        if link not in self.visited:
                            await self.queue.put(link)

                # Tell the queue this task is finished
                self.queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Worker {name} encountered an error: {e}")
                self.queue.task_done()

    async def crawl(self):
        """The main entry point that starts the crawler."""
        start_time = time.perf_counter()
        
        # Seed the queue with our starting URLs
        for url in SEED_URLS:
            self.queue.put_nowait(url)

        # Open a single persistent HTTP session (much faster than opening a new one per request)
        async with aiohttp.ClientSession() as session:
            # Create our concurrent worker tasks
            workers = [
                asyncio.create_task(self.worker(f"Worker-{i}", session))
                for i in range(MAX_CONCURRENT_REQUESTS)
            ]

           # Wait until we hit our page limit
            while len(self.visited) < MAX_PAGES_TO_CRAWL:
                # We simply wait. The workers will continuously add thousands of new links
                # to the queue as they parse the Wikipedia pages.
                await asyncio.sleep(0.5)
            # Cancel all workers once we're done
            for w in workers:
                w.cancel()

            elapsed = time.perf_counter() - start_time
            logging.info(f"Crawling finished. Crawled {len(self.crawled_data)} pages in {elapsed:.2f} seconds.")
            return self.crawled_data

if __name__ == "__main__":
    # This block allows us to run this file directly to test the crawler
    spider = AsyncSpider()
    
    # Run the asynchronous crawl method
    data = asyncio.run(spider.crawl())
    
    # Print the first URL we successfully crawled to prove it worked
    if data:
        print("\nSuccess! First crawled page URL:", data[0]['url'])
        print("HTML length:", len(data[0]['html']))