import json
import httpx
import logging
from pathlib import Path
from typing import List, Optional, Dict
from difflib import get_close_matches

logging.basicConfig(
    filename='library.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"

class Library:
    def __init__(self, file_path: str = "library.json"):
        self.file_path = Path(file_path)
        self.books: List[Book] = []
        self._api_cache = {}  # API yanıtlarını önbelleğe almak için
        self.load_books()

    # JSON Operations
    def load_books(self):
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.books = [Book(**item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            self.books = []

    def save_books(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump([b.__dict__ for b in self.books], f, indent=2)

    # Core Methods
    def add_book(self, book: Book) -> bool:
        """Kitap eklerken tüm ISBN varyasyonlarını kontrol et"""
        # Kitabın zaten var olup olmadığını kontrol et
        for existing_book in self.books:
            if book.isbn == existing_book.isbn or book.title.lower() == existing_book.title.lower():
                return False
        
        self.books.append(book)
        self.save_books()
        return True

    def remove_book(self, isbn: str):
        book = self.find_book(isbn)
        if book:
            self.books.remove(book)
            self.save_books()
            return True
        return False

    def list_books(self):
        return [str(book) for book in self.books]

    def find_book(self, query: str) -> Optional[Book]:
        query = query.lower()
        for book in self.books:
            if query in (book.isbn.lower(), book.title.lower(), book.author.lower()):
                return book
        
        matches = get_close_matches(query, [b.title for b in self.books], n=3, cutoff=0.4)
        if matches:
            print("Benzer kitaplar:")
            for match in matches:
                print(f"- {match}")
        return None

    # API Integration
    async def fetch_book_from_api(self, isbn: str) -> Optional[Book]:
        """ISBN ile kitap bilgisi getirir (tüm sorunlar giderildi)"""
        cleaned_isbn = ''.join(c for c in isbn if c.isdigit())
        if not cleaned_isbn or len(cleaned_isbn) not in (10, 13):
            print("⚠️ Geçersiz ISBN formatı (10 veya 13 rakam olmalı)")
            return None

        # Önce önbelleği kontrol et
        for cached_isbn, book in self._api_cache.items():
            if cleaned_isbn in [cached_isbn, book.isbn]:
                return book

        try:
            # Open Library'yi dene (302 yönlendirmelerini takip et)
            async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
                response = await client.get(f"https://openlibrary.org/isbn/{cleaned_isbn}.json")
                if response.status_code == 404:
                    return None
                    
                data = response.json()
                
                # ISBN'leri topla (10 ve 13 haneli)
                isbns = set()
                isbns.add(cleaned_isbn)
                if "isbn_10" in data:
                    isbns.update(data["isbn_10"])
                if "isbn_13" in data:
                    isbns.update(data["isbn_13"])
                
                # Aynı kitabın diğer ISBN'lerini kontrol et
                for existing_isbn in isbns:
                    if existing_isbn in self._api_cache:
                        return self._api_cache[existing_isbn]
                
                # Yazar bilgisi
                author = "Bilinmeyen Yazar"
                if "authors" in data:
                    if isinstance(data["authors"][0], dict):
                        author = data["authors"][0].get("name", author)
                    elif isinstance(data["authors"][0], str):
                        author = data["authors"][0]
                
                # Kitap nesnesi oluştur
                book = Book(
                    title=data.get("title", f"Bilinmeyen (ISBN: {cleaned_isbn})"),
                    author=author,
                    isbn=cleaned_isbn
                )
                
                # Tüm ISBN'leri önbelleğe ekle
                for isbn_num in isbns:
                    self._api_cache[isbn_num] = book
                    
                return book
                
        except httpx.RequestError as e:
            logging.error(f"OpenLibrary API hatası (ISBN: {cleaned_isbn}): {str(e)}")
            print(f"⚠️ API bağlantı hatası: {str(e)}")
        except Exception as e:
            logging.error(f"Beklenmeyen hata (ISBN: {cleaned_isbn}): {str(e)}")
            print(f"⚠️ İşlem hatası: {str(e)}")
        
        return None

    async def _try_open_library(self, isbn: str) -> Optional[Book]:
        """Open Library API denemesi (geliştirilmiş)"""
        url = f"https://openlibrary.org/isbn/{isbn}.json"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                
                if response.status_code == 404:
                    return None
                    
                response.raise_for_status()
                data = response.json()
                
                # Debug için ham veriyi logla
                logging.debug(f"OpenLibrary API Yanıtı: {data}")
                
                title = data.get("title", f"Bilinmeyen (ISBN: {isbn})")
                
                # Yazar bilgisi için gelişmiş çözüm
                author = "Bilinmeyen Yazar"
                if "authors" in data and data["authors"]:
                    first_author = data["authors"][0]
                    if isinstance(first_author, dict):
                        author = first_author.get("name", author)
                    elif isinstance(first_author, str):
                        author = first_author
                    elif "key" in first_author:
                        author_url = f"https://openlibrary.org{first_author['key']}.json"
                        author_res = await client.get(author_url)
                        if author_res.status_code == 200:
                            author_data = author_res.json()
                            author = author_data.get("name", author)
                
                return Book(title, author, isbn)
                
        except httpx.RequestError as e:
            logging.warning(f"OpenLibrary ağ hatası: {str(e)}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(f"OpenLibrary veri hatası: {str(e)}")
            return None

    async def _try_google_books(self, isbn: str) -> Optional[Book]:
        """Google Books API yedek kaynak"""
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                data = response.json()
                
                if data.get("totalItems", 0) > 0:
                    item = data["items"][0]["volumeInfo"]
                    return Book(
                        title=item.get("title", "Bilinmeyen"),
                        author=", ".join(item.get("authors", ["Bilinmeyen Yazar"])),
                        isbn=isbn
                    )
        except Exception:
            return None