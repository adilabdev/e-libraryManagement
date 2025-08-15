class BookNotFoundError(Exception):
    """Kitap bulunamadığında fırlatılır"""
    pass

class APIError(Exception):
    """API çağrısı başarısız olduğunda fırlatılır"""
    pass