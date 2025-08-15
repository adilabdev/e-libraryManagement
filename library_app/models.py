import json
import httpx
from pathlib import Path
from typing import List, Optional, Dict
from difflib import get_close_matches

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

    # API Integration
    async def fetch_book_from_api(self, isbn: str) -> Optional[Book]:
        cleaned_isbn = isbn.strip().replace("-", "")
        if not cleaned_isbn.isdigit() or len(cleaned_isbn) not in (10, 13):
            print("Geçersiz ISBN formatı")
            return None

        url = f"https://openlibrary.org/isbn/{cleaned_isbn}.json"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                
                if response.status_code == 404:
                    print("Kitap bulunamadı")
                    return None
                    
                data = response.json()
                
                title = data.get("title", f"Bilinmeyen (ISBN: {cleaned_isbn})")
                authors = data.get("authors", [{"name": "Bilinmeyen Yazar"}])
                author = authors[0].get("name", "Bilinmeyen Yazar") if authors else "Bilinmeyen Yazar"
                
                return Book(title, author, cleaned_isbn)
                
        except httpx.RequestError as e:
            print(f"API bağlantı hatası: {e}")
        except json.JSONDecodeError:
            print("Geçersiz API yanıtı")
        except Exception as e:
            print(f"Beklenmeyen hata: {type(e).__name__}")
        
        return None