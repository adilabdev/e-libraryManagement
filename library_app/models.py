import httpx
import json
from pathlib import Path
from typing import List, Optional
from difflib import get_close_matches

class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn

    def __str__(self):
        return f"'{self.title}' by {self.author} (ISBN: {self.isbn})"

class Library:
    def __init__(self, db_file: str = "library.json"):
        self.db_file = Path(db_file)
        self.books: List[Book] = []
        self._load_books()

    def _load_books(self):
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.books = [Book(**item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            self.books = []

    def _save_books(self):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump([b.__dict__ for b in self.books], f, indent=2)

    def add_book(self, book: Book) -> bool:
        if not any(b.isbn == book.isbn for b in self.books):
            self.books.append(book)
            self._save_books()
            print(f"✅ Kitap eklendi: {book.title}")
            return True
        print("⚠️ Bu ISBN zaten kayıtlı!")
        return False

    def list_books(self) -> None:
        if not self.books:
            print("\n📚 Kütüphane boş")
            return
        print("\n📚 KÜTÜPHANE KİTAPLARI:")
        for i, book in enumerate(self.books, 1):
            print(f"{i}. {book}")

    def remove_book(self, isbn: str) -> bool:
        for book in self.books:
            if book.isbn == isbn:
                self.books.remove(book)
                self._save_books()
                print(f"❌ Kitap silindi: {book.title}")
                return True
        print("⚠️ Kitap bulunamadı")
        return False

    def find_book(self, query: str) -> Optional[Book]:
        query = query.lower()
        for book in self.books:
            if query in (book.isbn.lower(), book.title.lower(), book.author.lower()):
                return book
        
        matches = get_close_matches(query, [b.title.lower() for b in self.books], n=3, cutoff=0.4)
        if matches:
            print("\n🔍 Benzer kitaplar:")
            for title in matches:
                print(f"- {title}")
        return None

    async def fetch_book_from_api(self, isbn: str) -> Optional[Book]:
        cleaned_isbn = isbn.replace("-", "").strip()
        if not cleaned_isbn.isdigit():
            print("⚠️ Geçersiz ISBN formatı (sadece rakam ve tire içermeli)")
            return None

        url = f"https://openlibrary.org/isbn/{cleaned_isbn}.json"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                
                if response.status_code == 404:
                    print("⚠️ Kitap bulunamadı (Geçersiz ISBN)")
                    return None
                    
                data = response.json()
                
                title = data.get("title", "Bilinmeyen Başlık")
                authors = data.get("authors", [{"name": "Bilinmeyen Yazar"}])
                author = authors[0].get("name", "Bilinmeyen Yazar") if authors else "Bilinmeyen Yazar"
                
                return Book(title, author, cleaned_isbn)
                
        except httpx.RequestError as e:
            print(f"⚠️ Ağ hatası: {e}")
        except json.JSONDecodeError:
            print("⚠️ Geçersiz API yanıtı")
        except Exception as e:
            print(f"⚠️ Beklenmeyen hata: {type(e).__name__}: {e}")
            
        return None