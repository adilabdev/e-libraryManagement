import asyncio
from library_app.models import Book, Library

async def main():
    lib = Library()
    
    while True:
        print("\n📚 KÜTÜPHANE YÖNETİMİ")
        print("1. Kitap Ekle (Manuel)")
        print("2. Kitap Ekle (ISBN ile)")
        print("3. Kitap Sil")
        print("4. Kitapları Listele")
        print("5. Kitap Ara")
        print("6. Çıkış")
        
        choice = input("Seçiminiz: ").strip()
        
        if choice == "1":
            title = input("Kitap Adı: ").strip()
            author = input("Yazar: ").strip()
            isbn = input("ISBN: ").strip()
            if lib.add_book(Book(title, author, isbn)):
                print("Kitap eklendi!")
            else:
                print("Bu ISBN zaten kayıtlı!")
                
        elif choice == "2":
            isbn = input("ISBN: ").strip()
            if book := await lib.fetch_book_from_api(isbn):
                if lib.add_book(book):
                    print(f"Kitap eklendi: {book.title}")
                else:
                    print("Bu ISBN zaten kayıtlı!")
        
        elif choice == "3":
            isbn = input("Silinecek ISBN: ").strip()
            if lib.remove_book(isbn):
                print("Kitap silindi!")
            else:
                print("Kitap bulunamadı!")
                
        elif choice == "4":
            books = lib.list_books()
            if books:
                print("\n📚 KİTAP LİSTESİ:")
                for i, book in enumerate(books, 1):
                    print(f"{i}. {book}")
            else:
                print("Kütüphane boş!")
                
        elif choice == "5":
            query = input("Arama (ISBN/Ad/Yazar): ").strip()
            if book := lib.find_book(query):
                print(f"\nBulunan Kitap: {book}")
        
        elif choice == "6":
            print("Çıkış yapılıyor...")
            break
            
        else:
            print("Geçersiz seçim!")

if __name__ == "__main__":
    asyncio.run(main())