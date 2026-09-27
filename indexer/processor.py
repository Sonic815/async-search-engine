# indexer/processor.py
import re
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download the NLTK stop words dictionary (only downloads once)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextProcessor:
    def __init__(self):
        # Load English stop words ("the", "is", "in", etc.)
        self.stop_words = set(stopwords.words('english'))
        # Initialize the stemmer (turns "running" into "run")
        self.stemmer = PorterStemmer()

    def clean_html(self, html: str) -> str:
        """Removes HTML tags, JavaScript, and CSS to extract pure text."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove script and style elements completely
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.extract()
            
        # Get the raw text
        text = soup.get_text(separator=' ')
        return text

    def process_text(self, text: str) -> list:
        """Cleans the text and converts it into a list of normalized tokens."""
        # 1. Convert to lowercase
        text = text.lower()
        
        # 2. Remove all punctuation and numbers (keep only letters)
        # We use a Regular Expression (Regex) for this
        text = re.sub(r'[^a-z\s]', '', text)
        
        # 3. Tokenize (split into a list of words)
        words = text.split()
        
        # 4. Remove stop words and apply stemming
        cleaned_words = []
        for word in words:
            if word not in self.stop_words:
                stemmed_word = self.stemmer.stem(word)
                cleaned_words.append(stemmed_word)
                
        return cleaned_words

    def get_tokens_from_html(self, html: str) -> list:
        """Master function that takes raw HTML and returns clean NLP tokens."""
        raw_text = self.clean_html(html)
        return self.process_text(raw_text)

# Quick test block
if __name__ == "__main__":
    sample_html = "<html><body><h1>Machine Learning!</h1><p>The algorithms are running quickly in 2026.</p></body></html>"
    processor = TextProcessor()
    tokens = processor.get_tokens_from_html(sample_html)
    print("Original HTML:", sample_html)
    print("Cleaned NLP Tokens:", tokens)