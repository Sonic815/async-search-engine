# Crawler settings
MAX_CONCURRENT_REQUESTS = 10  # We can go faster now!
MAX_PAGES_TO_CRAWL = 100      # 100 pages is a great test for the open web

# Seed URLs (Let's start at tech aggregators that link to thousands of random sites)
SEED_URLS = [
    "https://news.ycombinator.com/",          # Hacker News (Links to tech articles everywhere)
    "https://github.com/trending",            # Trending GitHub repos
    "https://arstechnica.com/"                # Tech news site
]

# Identify ourselves professionally so web admins don't block us as a malicious attack
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AnveshanBot/1.0; +http://yourwebsite.com)"
}