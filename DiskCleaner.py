#!/usr/bin/env python3

# Ten plik jest głównym punktem wejścia do aplikacji DiskCleaner.
# Jego jedynym zadaniem jest zaimportowanie i uruchomienie
# funkcji main() z modułu interfejsu linii poleceń (cli).
# Taka struktura (tzw. "runner" lub "entry-point script") jest
# dobrą praktyką, ponieważ oddziela logikę aplikacji od
# samego mechanizmu jej uruchamiania.

# Importujemy funkcję 'main' z naszego pakietu 'src.cli'.
# Użycie 'src.cli' jest możliwe dzięki temu, że Python
# traktuje katalog 'src' jako pakiet (dzięki przyszłemu
# plikowi __init__.py, choć w Pythonie 3 nie jest on zawsze
# wymagany do tego celu).
from src.cli import main

if __name__ == "__main__":
    # Wywołanie głównej funkcji aplikacji.
    # Ten warunek (__name__ == "__main__") jest prawdziwy tylko wtedy,
    # gdy plik jest uruchamiany bezpośrednio przez interpretera Pythona,
    # a nie gdy jest importowany jako moduł do innego skryptu.
    # To standardowy i zalecany sposób na tworzenie wykonywalnych
    # skryptów w Pythonie.
    main()
