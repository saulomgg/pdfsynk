# ---------------------------------------------------------
# PdfSynk - Ferramenta Oficial HubSynk
# Versão: V.1.0
# Desenvolvido por: saulomgg (https://github.com/saulomgg)
# ---------------------------------------------------------

import tkinter as tk
from ui.app import PdfSynkApp

def main():
    root = tk.Tk()
    app = PdfSynkApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
