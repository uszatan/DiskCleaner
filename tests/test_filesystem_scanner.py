import unittest
import os
import tempfile
import shutil
from src.filesystem_scanner import scan_filesystem
from src.definitions import sScannerObject

class TestFilesystemScanner(unittest.TestCase):
    """
    Zestaw testów jednostkowych dla funkcji scan_filesystem.
    Testy te weryfikują, czy skaner poprawnie identyfikuje pliki i katalogi
    oraz generuje dla nich odpowiednie obiekty sScannerObject.
    """

    def setUp(self):
        """
        Metoda wywoływana przed każdym testem.
        Tworzy tymczasową strukturę katalogów i plików, która posłuży jako
        środowisko testowe dla skanera.
        """
        # Utworzenie unikalnego katalogu tymczasowego.
        self.test_dir = tempfile.mkdtemp()
        # Struktura do utworzenia:
        # test_dir/
        #   |- file1.txt
        #   |- empty_dir/
        #   |- sub_dir/
        #      |- file2.txt
        #      |- file3.log
        self.structure = {
            "file1.txt": "content1",
            "empty_dir": None,
            "sub_dir": {
                "file2.txt": "content2",
                "file3.log": "log_content"
            }
        }
        # Wywołanie pomocniczej funkcji do fizycznego utworzenia tej struktury.
        self._create_test_structure(self.test_dir, self.structure)

    def _create_test_structure(self, base_path, structure):
        """
        Pomocnicza, rekurencyjna funkcja do tworzenia plików i katalogów.
        """
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            if content is None:
                # Jeśli content jest None, tworzymy pusty katalog.
                os.makedirs(path)
            elif isinstance(content, dict):
                # Jeśli content jest słownikiem, tworzymy katalog i wchodzimy rekurencyjnie.
                os.makedirs(path)
                self._create_test_structure(path, content)
            else:
                # W przeciwnym razie tworzymy plik z zadaną zawartością.
                with open(path, "w") as f:
                    f.write(content)

    def tearDown(self):
        """
        Metoda wywoływana po każdym teście.
        Usuwa cały tymczasowy katalog wraz z jego zawartością,
        aby nie pozostawiać śmieci w systemie.
        """
        shutil.rmtree(self.test_dir)

    def test_scan_filesystem(self):
        """
        Główny test dla funkcji skanującej.
        Założenia: Istnieje predefiniowana struktura plików i katalogów.
        Scenariusz: Wywołanie funkcji scan_filesystem na tej strukturze.
        Oczekiwany wynik: Generator powinien zwrócić poprawną liczbę obiektów
                         sScannerObject, a ich atrybuty (nazwa, typ, rozmiar)
                         powinny zgadzać się z rzeczywistością.
        """
        # Uruchomienie skanera na naszym tymczasowym katalogu.
        # Wyniki konwertujemy na listę, aby móc łatwo je analizować.
        results = list(scan_filesystem(self.test_dir))

        # Oczekujemy znalezienia 5 obiektów: 2 katalogów i 3 plików.
        self.assertEqual(len(results), 5, "Skaner powinien znaleźć 5 obiektów (3 pliki i 2 katalogi).")

        # Tworzymy słownik, gdzie kluczem jest nazwa obiektu, a wartością sam obiekt.
        # Ułatwi to weryfikację poszczególnych elementów.
        results_map = {os.path.join(r.objPathId, r.objName) if r.objIsDir == 0 else r.objName: r for r in results}
        
        # Weryfikacja katalogów
        self.assertIn('empty_dir', results_map)
        self.assertTrue(results_map['empty_dir'].objIsDir, "Obiekt 'empty_dir' powinien być katalogiem.")
        
        self.assertIn('sub_dir', results_map)
        self.assertTrue(results_map['sub_dir'].objIsDir, "Obiekt 'sub_dir' powinien być katalogiem.")

        # Weryfikacja plików
        # Sprawdzamy, czy 'file1.txt' został poprawnie zidentyfikowany jako plik.
        path_file1 = os.path.join(results_map['sub_dir'].objPathId, 'file1.txt')
        self.assertIn(path_file1, results_map)
        self.assertFalse(results_map[path_file1].objIsDir, "Obiekt 'file1.txt' powinien być plikiem.")
        self.assertEqual(results_map[path_file1].objSize, len("content1"), "Rozmiar 'file1.txt' się nie zgadza.")

        # Sprawdzamy 'file2.txt' w podkatalogu.
        path_file2 = os.path.join(results_map['sub_dir'].objId, 'file2.txt')
        self.assertIn(path_file2, results_map)
        self.assertFalse(results_map[path_file2].objIsDir, "Obiekt 'file2.txt' powinien być plikiem.")
        self.assertEqual(results_map[path_file2].objSize, len("content2"), "Rozmiar 'file2.txt' się nie zgadza.")
        
        # Sprawdzamy 'file3.log' w podkatalogu.
        path_file3 = os.path.join(results_map['sub_dir'].objId, 'file3.log')
        self.assertIn(path_file3, results_map)
        self.assertFalse(results_map[path_file3].objIsDir, "Obiekt 'file3.log' powinien być plikiem.")
        self.assertEqual(results_map[path_file3].objSize, len("log_content"), "Rozmiar 'file3.log' się nie zgadza.")


if __name__ == '__main__':
    unittest.main()
