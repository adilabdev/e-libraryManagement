from difflib import get_close_matches
import httpx
import json
from pathlib import Path
from typing import List, Optional, Dict

class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn

    def __str__(self):
        return f"'{self.title}' by {self.author} (ISBN: {self.isbn})"

class Library:
    def __init__(self, db_file: str = "library_db.json"):
        self.db_file = Path(db_file)
        self.books: List[Book] = []
        self._load_books()

    # Veritabanı İşlemleri
    def _load_books(self):
        if self.db_file.exists():
            with open(self.db_file, 'r') as f:
                data = json.load(f)
                self.books = [Book(**item) for item in data]

    def _save_books(self):
        with open(self.db_file, 'w') as f:
            json.dump([b.__dict__ for b in self.books], f, indent=2)

    # Kütüphane İşlemleri
    def add_book(self, book: Book):
        self.books.append(book)
        self._save_books()
        print(f"✅ Kitap eklendi: {book.title}")

    def list_books(self):  # <-- EKSİK METOD EKLENDİ
        if not self.books:
            print("Kütüphane boş.")
            return
        print("\n📚 KÜTÜPHANE KİTAPLARI:")
        for i, book in enumerate(self.books, 1):
            print(f"{i}. {book}")

    def remove_book(self, isbn: str):
        for book in self.books:
            if book.isbn == isbn:
                self.books.remove(book)
                self._save_books()
                print(f"❌ Kitap silindi: {book.title}")
                return
        print("Kitap bulunamadı.")

    def find_book(self, query: str):
        for book in self.books:
            if query.lower() in (book.isbn.lower(), book.title.lower(), book.author.lower()):
                return book
        self._suggest_books(query)
        return None

    def _suggest_books(self, query: str):
        titles = [b.title for b in self.books]
        matches = get_close_matches(query, titles, n=3, cutoff=0.4)
        if matches:
            print("\n🔍 Benzer kitaplar:")
            for title in matches:
                print(f"- {title}")

    # API İşlemleri
    async def add_book_by_isbn(self, isbn: str):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"https://openlibrary.org/isbn/{isbn}.json")
                data = response.json()
                book = Book(
                    title=data.get("title", "Bilinmeyen"),
                    author=data.get("authors", [{"name": "Bilinmeyen"}])[0]["name"],
                    isbn=isbn
                )
                self.add_book(book)
                return book
            except Exception as e:
                print(f"⚠️ Hata: {e}")
                return None



    async def fetch_book_from_api(self, isbn: str) -> Optional[Book]:
    # 1. ISBN Temizleme
        cleaned_isbn = "".join(c for c in isbn if c.isdigit())
    
    # 2. Uzunluk Kontrolü
        if len(cleaned_isbn) not in (10, 13):
            print("⚠️ ISBN 10 veya 13 haneli olmalıdır")
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
            # 3. Kitap Bilgisi
                book_url = f"https://openlibrary.org/isbn/{cleaned_isbn}.json"
                book_res = await client.get(book_url)
            
                if book_res.status_code == 404:
                    print(f"⚠️ Bu ISBN ile kitap bulunamadı: {cleaned_isbn}")
                    return None
                
                book_data = book_res.json()
            
                # 4. Yazar Detayı (Ek İstek)
                author_name = "Bilinmeyen Yazar"
                if "authors" in book_data:
                    author_url = f"https://openlibrary.org{book_data['authors'][0]['key']}.json"
                    author_res = await client.get(author_url)
                    if author_res.status_code == 200:
                        author_data = author_res.json()
                        author_name = author_data.get("name", author_name)
            
                # 5. Kitap Nesnesi Oluşturma
                return Book(
                    title=book_data.get("title", "Bilinmeyen Başlık"),
                    author=author_name,
                    isbn=cleaned_isbn
            )
            
        except httpx.RequestError:
            print("⚠️ API'ye bağlanılamadı (internet bağlantınızı kontrol edin)")
        except json.JSONDecodeError:
            print("⚠️ API geçersiz yanıt verdi")
        except Exception as e:
            print(f"⚠️ Beklenmeyen hata: {type(e).__name__}")
    
        return None