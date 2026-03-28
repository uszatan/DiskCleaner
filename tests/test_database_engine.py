import unittest
import os
import sqlite3
from src.database_engine import DatabaseEngine
from src.definitions import sScannerObject

class TestDatabaseEngine(unittest.TestCase):
    """
    Zestaw testów jednostkowych dla klasy DatabaseEngine.
    Testy te weryfikują poprawność operacji na bazie danych, takich jak
    tworzenie schematu, wstawianie obiektów i wyszukiwanie duplikatów.
    """

    def setUp(self):
        """
        Metoda wywoływana przed każdym testem.
        Przygotowuje środowisko testowe, tworząc tymczasową bazę danych w pamięci.
        Dzięki temu testy są odizolowane od siebie i nie zostawiają śladów w systemie plików.
        """
        # Definicja ścieżki do tymczasowej bazy danych. Używamy ':memory:',
        # co oznacza, że baza danych będzie istnieć tylko w pamięci RAM.
        self.db_path = ":memory:"
        # Inicjalizacja silnika bazy danych.
        self.db_engine = DatabaseEngine(self.db_path)
        # Utworzenie schematu przed każdym testem.
        self.db_engine.create_schema()
        # Przygotowanie listy przykładowych obiektów do testów.
        self.test_objects = [
            # Katalog root
            sScannerObject('docs', 0, 1, 1, 0, 0, None),
            # Plik w katalogu root
            sScannerObject('file1.txt', 1, 1, 0, 1024, 1678886400, None),
            # Duplikat pliku file1.txt (ta sama nazwa, rozmiar, timestamp)
            sScannerObject('file1.txt', 1, 2, 0, 1024, 1678886400, None),
            # Inny plik, ale z tą samą nazwą (inny rozmiar)
            sScannerObject('file1.txt', 1, 3, 0, 2048, 1678886400, None),
            # Unikalny plik
            sScannerObject('unique.txt', 1, 4, 0, 512, 1678886401, None)
        ]

    def test_create_schema(self):
        """
        Testuje, czy schemat bazy danych jest tworzony poprawnie.
        Założenia: Baza danych jest pusta.
        Scenariusz: Wywołanie metody create_schema().
        Oczekiwany wynik: W bazie danych istnieją tabele 'scanned_objects' i 'import_log'.
        """
        # Nawiązanie połączenia z bazą danych w pamięci.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Zapytanie do wewnętrznej tabeli SQLite, która przechowuje informacje o schemacie.
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scanned_objects'")
        # Sprawdzenie, czy tabela 'scanned_objects' została znaleziona.
        self.assertIsNotNone(cursor.fetchone(), "Tabela 'scanned_objects' nie została utworzona.")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='import_log'")
        # Sprawdzenie, czy tabela 'import_log' została znaleziona.
        self.assertIsNotNone(cursor.fetchone(), "Tabela 'import_log' nie została utworzona.")
        conn.close()

    def test_insert_scanner_objects(self):
        """
        Testuje, czy obiekty są poprawnie wstawiane do bazy danych.
        Założenia: Baza danych jest pusta, schemat istnieje.
        Scenariusz: Wstawienie listy predefiniowanych obiektów.
        Oczekiwany wynik: W tabeli 'scanned_objects' znajduje się dokładnie tyle wierszy,
                         ile obiektów zostało wstawionych.
        """
        # Generator na podstawie listy testowych obiektów.
        objects_generator = (obj for obj in self.test_objects)
        # Wywołanie metody wstawiającej obiekty.
        self.db_engine.insert_scanner_objects(objects_generator, "test/path")

        # Weryfikacja
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Zliczenie wierszy w tabeli.
            cursor.execute("SELECT COUNT(*) FROM scanned_objects")
            count = cursor.fetchone()[0]
            # Sprawdzenie, czy liczba wierszy zgadza się z liczbą wstawionych obiektów.
            self.assertEqual(count, len(self.test_objects), "Liczba wstawionych obiektów nie zgadza się.")

    def test_find_duplicate_candidates(self):
        """
        Testuje logikę wyszukiwania kandydatów na duplikaty.
        Założenia: Baza danych zawiera zestaw plików, w tym duplikaty.
        Scenariusz: Wywołanie metody find_duplicate_candidates().
        Oczekiwany wynik: Metoda powinna zwrócić jedną grupę duplikatów,
                         która pasuje do 'file1.txt' (ta sama nazwa, rozmiar i timestamp).
        """
        # Wstawienie danych testowych.
        objects_generator = (obj for obj in self.test_objects)
        self.db_engine.insert_scanner_objects(objects_generator, "test/path")

        # Wywołanie metody wyszukującej duplikaty.
        duplicates = self.db_engine.find_duplicate_candidates()

        # Weryfikacja
        # Oczekujemy znalezienia jednej grupy duplikatów.
        self.assertEqual(len(duplicates), 1, "Powinna zostać znaleziona jedna grupa duplikatów.")
        # Rozpakowanie wyników.
        name, size, timestamp, count = duplicates[0]
        # Sprawdzenie, czy dane duplikatu zgadzają się z oczekiwaniami.
        self.assertEqual(name, "file1.txt")
        self.assertEqual(size, 1024)
        self.assertEqual(timestamp, 1678886400)
        # Oczekujemy, że w grupie będą 2 pliki.
        self.assertEqual(count, 2, "Grupa duplikatów powinna zawierać 2 pliki.")

if __name__ == '__main__':
    unittest.main()
