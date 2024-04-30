from pathlib import Path
from datetime import date, datetime, timedelta

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf
import tkinter.messagebox as mbox
from tkinter.filedialog import asksaveasfilename

from tkpdfviewer import ShowPdf



class TranscribeGui():

    #################################################################
    # ...
    PHRASEN = "[NAME]", "[NICHT_LESBAR]", "[KEIN_EINTRAG]"
    def btn_name(self):
        self.transcribed_txt.insert(tk.INSERT, TranscribeGui.PHRASEN[0])
    def btn_nicht_lesbar(self):
        self.transcribed_txt.insert(tk.INSERT, TranscribeGui.PHRASEN[1])
    def btn_kein_eintrag(self):
        self.transcribed_txt.insert(tk.INSERT, TranscribeGui.PHRASEN[2])

    #################################################################

    def showPdfContainer(self, elemroot):
        spdf = ShowPdf()
        pdfview = spdf.pdf_view(
            elemroot,
            pdf_location=str(self.pdffilepath.absolute()),
            width=100,  # %?
            bar=False,
            load=None,  # ?
        )
        return pdfview

    #################################################################
    def btn_mein_ziel_clicked(self):
        self.txt_mein_ziel.delete("1.0", tk.END)
        self.txt_mein_ziel.insert("1.0", "[KEIN_EINTRAG]")


    #################################################################
    def berechne_woche(self, datum):
        montag = datum - timedelta(days=datum.weekday())
        freitag = montag + timedelta(days=4)
        return montag, freitag

    #################################################################
    def btn_berechne_woche_clicked(self):
        diw = self.txt_date_in_week.get("1.0", tk.END).strip()

        try:
            datum = datetime.strptime(diw, '%d.%m.%Y')
        except:
            mbox.showerror("FEHLER", "Datumskonversion fehlgeschlagen.\nFormat: TT.MM.JJJJ!")
            return

        montag, freitag = self.berechne_woche(datum)
        woche_str = f'{montag.strftime("%d.%m.%Y")} - {freitag.strftime("%d.%m.%Y")}'

        self.txt_woche.delete("1.0", tk.END)
        self.txt_woche.insert("1.0", woche_str)


    #################################################################
    def btn_wochenblock(self):

        DOW_DE = ["Mo", "Di", "Mi", "Do", "Fr"]  # benötigte Wochentage

        diw = self.txt_date_in_week.get("1.0", tk.END).strip()
        try:
            datum = datetime.strptime(diw, '%d.%m.%Y')
        except:
            mbox.showerror("FEHLER", 'Datumskonversion fehlgeschlagen,\nFeld "Datum in der Woche".\n\nFormat: TT.MM.JJJJ!')
            return

        montag, freitag = self.berechne_woche(datum)

        wochenblock = f'\nMein Ziel: {self.txt_mein_ziel.get("1.0",tk.END).strip()}\n\n'

        for i, wkdy in enumerate(DOW_DE):
            curdate = montag + timedelta(days=i)
            wochenblock += f'{wkdy} {curdate.strftime("%d.%m.%Y")}\n\n\n'

        self.transcribed_txt.insert(tk.INSERT, wochenblock)

    #################################################################
    def btn_meta_block(self):

        meta_block = f'''---
Identifier: {self.identifier}
Date: {self.txt_datum.get("1.0",tk.END).strip()}
---
'''
        self.transcribed_txt.insert("1.0", meta_block)

    #################################################################
    def prepare_texts(self):
        text_to_save = self.transcribed_txt.get("1.0", tk.END).strip()
        # metadaten entfernen
        plain_text = text_to_save.strip()
        for p in TranscribeGui.PHRASEN:
            plain_text = plain_text.replace(p, "")

        return text_to_save, plain_text

    #################################################################
    def btn_save_files(self):

        saves = {k: v for k, v in zip( ["Volle", "Reduzierte"], self.prepare_texts()) }

        for k, data in saves.items():
            save_targetname = asksaveasfilename(title=f"{k} Text-Datei zum Speichern auswählen...")
            with open(save_targetname, "w") as f: f.write(data)

    #################################################################
    def btn_save_files_defaultnames(self):

        full, stripped = self.prepare_texts()

        meta_file = Path(str(self.pdffilepath.parent) + "/" + self.identifier + "-meta.txt")
        plain_file = Path(str(self.pdffilepath.parent) + "/" + self.identifier + "-plain.txt")

        for f, data in [(meta_file, full), (plain_file, stripped)]:
            overwrite = True
            if f.exists():
                overwrite = mbox.askyesno("FEHLER", f'Die Datei "{str(f)}" existiert bereits!\nÜberschreiben?')
            if not overwrite: return

            with open(f, "w") as fh: fh.write(data)


    #################################################################
    def __init__(self, tkroot, pdffilename):

        self.tkroot = tkroot
        self.pdffilepath = Path(pdffilename)
        # ID
        self.identifier = str(self.pdffilepath.stem)
        tkroot.title(rf"Transkribiere: {pdffilename}")

        rootframe = tk.Frame(self.tkroot)

        # links PDF anzeigen
        left_frame = tk.Frame(rootframe, borderwidth=2, relief="solid")
        self.pdfview = self.showPdfContainer(elemroot=left_frame)
        self.pdfview.pack(padx=5, pady=5)
        #left_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        left_frame.grid(row=0, column=0, sticky="nsw")

        # rechts
        right_frame = tk.Frame(rootframe, borderwidth=2, relief="solid")
        #label_right = tk.Label(right_frame, text="RIGHT",).pack(padx=5, pady=5, expand=True, fill=tk.BOTH)
        #right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        #################################################################
        tk.Label(right_frame, text="Metadaten", font=tkf.Font(tkroot, size=15, weight=tkf.BOLD)).pack(fill=tk.X, side=tk.TOP)

        right_meta_frame = tk.Frame(right_frame)


        for idx, txt in enumerate(["Identifier", "Datum"]):
            tk.Label(right_meta_frame, text=txt).grid(row=idx, column=0)

        txt_id = tk.Text(right_meta_frame, height=1, width=60)
        txt_id.insert("1.0", self.identifier)
        txt_id.config(state=tk.DISABLED)
        txt_id.grid(row=0, column=1)

        self.txt_datum = tk.Text(right_meta_frame, height=1, width=60)
        self.txt_datum.grid(row=1, column=1)

        right_meta_frame.pack(fill=tk.X, side=tk.TOP)

        # Button "Metadatenblock anlegen"
        tk.Button(
            right_frame,
            text="Metadatatenblock am Anfang einfügen",
            command=self.btn_meta_block,
            font=tkf.Font(tkroot, size=15,),
        ).pack() #(fill=tk.X, side=tk.TOP)

        #################################################################
        tk.Label(right_frame, text="Wochen-Block", font=tkf.Font(tkroot, size=15, weight=tkf.BOLD)).pack(fill=tk.X, side=tk.TOP)

        # metadata frame, grid
        self.right_week_frame = tk.Frame(right_frame)

        # Textfelder etc.
        for idx, txt in enumerate(["Datum in der Woche", "Woche", "Mein Ziel"]):
            tk.Label(self.right_week_frame, text=txt).grid(row=idx, column=0)

        self.txt_date_in_week = tk.Text(self.right_week_frame, height=1, width=60)
        self.txt_date_in_week.grid(row=0, column=1)

        self.txt_woche = tk.Text(self.right_week_frame, height=1, width=60)
        self.txt_woche.grid(row=1, column=1)
        self.txt_mein_ziel = tk.Text(self.right_week_frame, height=1, width=60)
        self.txt_mein_ziel.grid(row=2, column=1)

        # Button: "Woche aus inliegendem Tag berechnen"
        #btn_berechne_woche = tk.Button(self.right_week_frame, text="Woche berechnen", command=self.btn_berechne_woche_clicked)
        #btn_berechne_woche.grid(row=0, column=2)
        tk.Button(self.right_week_frame, text="Woche berechnen", command=self.btn_berechne_woche_clicked).grid(row=0, column=2)

        # Button "Woche leeren"
        tk.Button(self.right_week_frame, text='<- leeren', command=lambda: self.txt_woche.delete("1.0", tk.END)).grid(row=1, column=2)

        # Button "kein eintrag" in mein Ziel
        tk.Button(self.right_week_frame, text='<- "kein Eintrag"', command=self.btn_mein_ziel_clicked).grid(row=2, column=2)

        self.right_week_frame.pack(fill=tk.X, side=tk.TOP)

        # Button "wochenblock anlegen
        tk.Button(
            right_frame,
            text="Wochenblock-Vorlage einfügen",
            command=self.btn_wochenblock,
            font=tkf.Font(tkroot, size=15,),
        ).pack() #(fill=tk.X, side=tk.TOP)

        #################################################################
        tk.Label(right_frame, text="Phrasen", font=tkf.Font(tkroot, size=15, weight=tkf.BOLD)).pack(fill=tk.X, side=tk.TOP)

        right_center_phrasen_frame = tk.Frame(right_frame, borderwidth=2, relief="solid")

        phrasen = {
            "[NAME]": self.btn_name,
            "[NICHT_LESBAR]": self.btn_nicht_lesbar,
            "[KEIN_EINTRAG]": self.btn_kein_eintrag,
        }

        for k, v in phrasen.items():
            tk.Button(right_center_phrasen_frame, text=k, command=v).pack(side=tk.LEFT)

        right_center_phrasen_frame.pack(fill=tk.X, side=tk.TOP)

        #################################################################
        tk.Label(right_frame, text="Transkribierter Text", font=tkf.Font(tkroot, size=15, weight=tkf.BOLD)).pack(fill=tk.X, side=tk.TOP)

        self.right_text_frame = tk.Frame(right_frame)
        # https://stackoverflow.com/questions/13832720/how-to-attach-a-scrollbar-to-a-text-widget
        self.transcribed_txt = tk.Text(self.right_text_frame, width=90)
        self.transcribed_txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        scrollb = ttk.Scrollbar(self.right_text_frame, command=self.transcribed_txt.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        self.transcribed_txt['yscrollcommand'] = scrollb.set

        self.right_text_frame.pack(fill=tk.BOTH, side=tk.TOP)

        frame_save_btns = tk.Frame(right_frame)

        tk.Button(
            frame_save_btns,
            text="Speichern mit Namensschema lt. Identifier",
            command=self.btn_save_files_defaultnames,
            font=tkf.Font(tkroot, size=12,),
        ).pack(side=tk.LEFT) #(fill=tk.X, side=tk.TOP)

        tk.Button(
            frame_save_btns,
            text="Speichern ... ",
            command=self.btn_save_files,
            font=tkf.Font(tkroot, size=12,),
        ).pack(side=tk.LEFT)

        frame_save_btns.pack(fill=tk.X, side=tk.TOP)

        #################################################################
        # rechts: "anzeigen"
        right_frame.grid(row=0, column=1, sticky="nsew")

        #################################################################
        # rootframe: Konfiguration
        rootframe.grid_columnconfigure(0, weight=1, uniform="group1")
        rootframe.grid_columnconfigure(1, weight=1, uniform="group1")
        rootframe.grid_rowconfigure(0, weight=1)
        # anzeigen
        rootframe.pack()
