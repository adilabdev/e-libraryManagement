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
        self._api_cache = {}
        self.load_books()

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

    def add_book(self, book: Book):
        if not any(b.isbn == book.isbn for b in self.books):
            self.books.append(book)
            self.save_books()
            return True
        return False

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

    async def fetch_book_from_api(self, isbn: str) -> Optional[Book]:
        cleaned_isbn = ''.join(c for c in isbn if c.isdigit())
        if len(cleaned_isbn) not in (10, 13) or not cleaned_isbn.isdigit():
            print("⚠️ Geçersiz ISBN formatı (10 veya 13 rakam olmalı)")
            return None

        if cleaned_isbn in self._api_cache:
            return self._api_cache[cleaned_isbn]

        try:
            # Önce Open Library'yi dene
            book = await self._try_open_library(cleaned_isbn)
            if not book:
                # Sonra Google Books'u dene
                book = await self._try_google_books(cleaned_isbn)
            
            if book:
                self._api_cache[cleaned_isbn] = book
                return book
            
            print(f"⚠️ Kitap bulunamadı (ISBN: {cleaned_isbn})")
            return None
                
        except Exception as e:
            logging.error(f"ISBN: {cleaned_isbn} - Hata: {str(e)}")
            print("⚠️ Kitap getirilirken hata oluştu (log kaydı oluşturuldu)")
            return None

    async def _try_open_library(self, isbn: str) -> Optional[Book]:
        url = f"https://openlibrary.org/isbn/{isbn}.json"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                data = response.json()
                
                title = data.get("title", f"Bilinmeyen (ISBN: {isbn})")
                author = "Bilinmeyen Yazar"
                if "authors" in data and data["authors"]:
                    if isinstance(data["authors"][0], dict):
                        author = data["authors"][0].get("name", author)
                    elif isinstance(data["authors"][0], str):
                        author = data["authors"][0]
                
                return Book(title, author, isbn)
        except (httpx.RequestError, json.JSONDecodeError, KeyError):
            return None

    async def _try_google_books(self, isbn: str) -> Optional[Book]:
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