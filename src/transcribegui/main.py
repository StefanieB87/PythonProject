import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from transcribegui import TranscribeGui

def gui_main():
    # PDF-Datei ermitteln
    pdfname = askopenfilename(title="PDF zur Transkription auswählen...")
    # Haupt-GUI
    root = tk.Tk()
    transcribegui = TranscribeGui(root, pdfname)
    root.mainloop()

if __name__ == '__main__':
    gui_main()
