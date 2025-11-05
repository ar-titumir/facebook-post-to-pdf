import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

from pdf_downloader import *

def create_pdf_from_post(link: str, pdf_name: str, pdf_dir: str):
    """
    Placeholder worker function.
    Replace the body of this function with your real logic that:
      - fetches image(s) from `link` (Facebook post)
      - creates a PDF saved as `pdf_name` (add .pdf if needed)
    This runs in a background thread.
    """
    # result_msg = create_pdf_from_post(link, pdf_name, pdf_dir)
    if not pdf_dir:
        pdf_dir = None
    if not pdf_name:
        pdf_name = None
    if "https://www.facebook.com/" in link:
        print("Running single post downloader")
        return run_a_single_link(link, pdf_dir, pdf_name)
    elif ".txt" in link:
        print("Running multiple posts downloader")
        return run_from_txt_file(link, pdf_dir)
    else:
        return "Link is Not Valid! "

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF file maker from facebook post image")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        frm = ttk.Frame(self)
        frm.grid(row=0, column=0, sticky="nsew")

        # Post link
        ttk.Label(frm, text="Post URL or Text File Dir:").grid(row=1, column=0, sticky="w", **pad)
        self.link_var = tk.StringVar()
        self.link_entry = ttk.Entry(frm, textvariable=self.link_var, width=60)
        self.link_entry.grid(row=1, column=1, **pad)
        self.link_entry.focus()

        # Post Links (.txt)
        # ttk.Label(frm, text="Post Links (.txt):").grid(row=1, column=0, sticky="w", **pad)
        # self.file_var = tk.StringVar()
        # self.file_entry = ttk.Entry(frm, textvariable=self.file_var, width=60)
        # self.file_entry.grid(row=1, column=1, **pad)

        # PDF file name
        ttk.Label(frm, text="PDF file name:").grid(row=2, column=0, sticky="w", **pad)
        self.pdf_var = tk.StringVar()
        self.pdf_entry = ttk.Entry(frm, textvariable=self.pdf_var, width=60)
        self.pdf_entry.grid(row=2, column=1, **pad)

        # PDF File Dir
        ttk.Label(frm, text="PDF File Dir:").grid(row=3, column=0, sticky="w", **pad)
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(frm, textvariable=self.dir_var, width=60)
        self.dir_entry.grid(row=3, column=1, **pad)


        # Run button
        self.run_btn = ttk.Button(frm, text="Run", command=self.on_run)
        self.run_btn.grid(row=4, column=0, columnspan=2, pady=(8,12))

        # Status label
        self.status_var = tk.StringVar(value="Idle")
        self.status_lbl = ttk.Label(frm, textvariable=self.status_var, foreground="blue")
        self.status_lbl.grid(row=5, column=0, columnspan=2, sticky="w", **pad)

    def on_run(self):
        link = self.link_var.get().strip()
        pdf_name = self.pdf_var.get().strip()
        pdf_dir = self.dir_var.get().strip()
        # file_path = self.file_var.get().strip()

        if not link:
            messagebox.showwarning("Validation", "Enter a Post URL or Text File Dir.")
            self.link_entry.focus()
            return

        if pdf_name and not pdf_name.lower().endswith(".pdf"):
            pdf_name = pdf_name + ".pdf"


        # disable UI controls while running
        self._set_running_state(True)
        self.status_var.set("Running...")

        # run worker in background thread
        thread = threading.Thread(target=self._run_worker, args=(link, pdf_name, pdf_dir), daemon=True)
        thread.start()

    def _set_running_state(self, running: bool):
        if running:
            self.run_btn.config(state="disabled")
            self.link_entry.config(state="disabled")
            self.pdf_entry.config(state="disabled")
        else:
            self.run_btn.config(state="normal")
            self.link_entry.config(state="normal")
            self.pdf_entry.config(state="normal")

    def _run_worker(self, link: str, pdf_name: str, pdf_dir: str):
        try:
            result_msg = create_pdf_from_post(link, pdf_name, pdf_dir)
            print(f"Downloader response: {result_msg}")
        except Exception as e:
            # marshal back to main thread to update UI
            print(f"Exception: {e}")
            self.after(0, self._on_worker_done, False, str(e))
        else:
            print(f"No Exception: {result_msg}")
            self.after(0, self._on_worker_done, True, result_msg)

    def _on_worker_done(self, success: bool, message: str):
        # re-enable UI
        self._set_running_state(False)
        self.status_var.set("Idle")

        if success:
            messagebox.showinfo("Success! ", message)
        else:
            messagebox.showerror("Error", f"Failed: {message}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
