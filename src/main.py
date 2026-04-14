import sys
import os

# Añadir el directorio raíz (padre de src) al sys.path para que los imports 'src.xxx' funcionen
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.app_ui import AppUI

if __name__ == "__main__":
    try:
        app = AppUI()
        app.mainloop()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        input("Presione Enter para salir...")
