# Async

A concurrent web crawler and semantic search engine. Async replaces traditional lexical keyword matching (TF-IDF) with a deep-learning architecture, using dense vector embeddings to understand the contextual meaning of search queries and web pages. 

The system leverages asynchronous I/O for rapid web scraping and a robust vector database for millisecond-latency similarity search, all wrapped in a responsive, Dockerized environment.

## Key Features
* **Semantic Search:** Uses the `all-MiniLM-L6-v2` transformer model to convert natural language sentences into high-dimensional vector embeddings, matching user intent rather than exact strings.
* **Vector Similarity Retrieval:** Implements FAISS (Facebook AI Similarity Search) to perform highly optimized nearest-neighbor distance calculations on the indexed data.
* **Concurrent Web Crawling:** Utilizes `asyncio` and `aiohttp` to fetch and parse HTML payloads concurrently without blocking the main API thread.
* **Modern Frontend Architecture:** A minimalist, dark-mode user interface styled with Tailwind CSS, featuring real-time DOM updates and geometric vector animations.
* **Containerized Infrastructure:** Fully Dockerized deployment with pre-compiled model weights and volume-mounting for live code synchronization.

## Tech Stack
* **Backend:** Python 3.11, FastAPI, Uvicorn, BeautifulSoup4
* **AI / Machine Learning:** Sentence-Transformers, FAISS-CPU, PyTorch
* **Frontend:** HTML5, Tailwind CSS, JavaScript
* **Infrastructure:** Docker

## Getting Started

### Prerequisites
* Docker Desktop installed and running.
* Git installed on your local machine.

### Installation & Deployment

1. **Clone the repository**
   Replace `YOUR_USERNAME` with your actual GitHub username before running this command:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/async-search-engine.git](https://github.com/YOUR_USERNAME/async-search-engine.git)
   cd async-search-engine