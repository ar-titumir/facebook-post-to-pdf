# 📸 Facebook Post Image to PDF Converter

This project provides a **GUI tool** and **automation backend** to convert **Facebook post images into a single high-quality PDF**.  
It supports **single post** or **bulk (.txt)** mode, **auto-login using cookies**, and even **AI-powered smart PDF naming** using your **[Gemini Local API](https://github.com/ar-titumir/gemini-local-api)**.

---

## ✨ Features

- 💻 **Simple GUI** to enter a Facebook post link or bulk `.txt` file  
- 🖼️ **Auto-download** all images from any public Facebook post  
- 📄 **Combine** them into a single, well-formatted and high-quality PDF file  
- 🧠 **Smart PDF naming:** Automatically generate a suitable PDF file name from the post caption using **Gemini Local API**  
- 🔐 **Uses cookies** for seamless Facebook login (no manual login required)  
- 🗂️ **Supports both single and batch processing** from a `.txt` file containing multiple post links  
- ⚡ **Threaded download** for faster performance  
- 📝 **Keeps a record** of already downloaded posts (`downloaded.txt`)  
- 📁 **Specify output directory** for saving generated PDF files  

---

## 🚀 How to Run

Make sure you have **Python** and **Google Chrome** installed.

### 1️⃣ Clone this repository
```bash
git clone https://github.com/ar-titumir/facebook-post-to-pdf.git
cd facebook-post-to-pdf
```

### 2️⃣ Create Virtual Environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt` yet, generate one using:
```bash
pip freeze > requirements.txt
```

---

## ⚙️ Prepare Facebook Cookies

Before running, log in to your Facebook account manually in Chrome, then export cookies to a file named:

```
fb1.txt
```

Place it inside the project directory.

Example cookie JSON:
```json
[
  {
    "name": "c_user",
    "value": "12345678",
    "domain": ".facebook.com"
  }
]
```

---

## 🧠 How to Enable Smart PDF Naming

To use **Gemini-based intelligent PDF naming**, first run your local Gemini API:

```bash
git clone https://github.com/ar-titumir/gemini-local-api
cd gemini-local-api
python app.py
```

Keep it running (default: `http://localhost:8000`).

When you run this tool, it will:
- Fetch each post’s caption  
- Send it to the Gemini Local API  
- Receive and use a generated, meaningful title for the PDF file  

### 💡 Example

If a Facebook post caption is:

> “A beautiful sunset at Cox’s Bazar 🌅”

The generated PDF name will be:

> `Beautiful_Sunset_CoxsBazar.pdf`

---

## ▶️ Run the App

Launch the GUI:

```bash
python app.py
```

You’ll see a window titled:

```
PDF file maker from facebook post image
```

### Input Fields:
1. **Post URL or Text File Dir:**  
   A single Facebook post link or a `.txt` file containing multiple links.  
2. **PDF File Name:**  
   Optional — if blank, Gemini will auto-generate a suitable name.  
3. **PDF File Dir:**  
   Optional — choose where to save your generated PDF.  

Then click **Run**. The downloader runs in the background and shows status updates.

---

## 🧩 Project Structure

| File / Folder        | Description                                                                 |
|----------------------|------------------------------------------------------------------------------|
| **app.py**           | Tkinter GUI — handles user input and launches background worker threads.     |
| **pdf_downloader.py**| Core logic for downloading, scraping, and PDF creation using Selenium + FPDF |
| **fb1.txt**          | Facebook cookie file (required for authentication)                           |
| **downloaded.txt**   | Keeps record of already downloaded posts to avoid duplicates                 |
| **/post_images**     | Temporary folder for downloaded images                                       |
| **/pdf_files**       | Output folder for generated PDFs                                             |

---

## 📦 Example Output

```
📁 post_images/
│   ├── 001.jpg
│   ├── 002.jpg
📁 pdf_files/
│   └── Beautiful_Sunset_CoxsBazar.pdf
📄 downloaded.txt
```

---

## ⚠️ Notes

- Ensure your Chrome version matches the Chrome Driver (handled automatically by `webdriver-manager`).
- Facebook cookies (`fb1.txt`) must be valid and up-to-date.
- Some private or restricted posts cannot be downloaded.
- Do not share your cookie file publicly for security reasons.

---

## 🤝 Contributing

Pull requests and feature suggestions are welcome!  
If you find this project useful, please ⭐ the repo and share feedback.  

---

## 📌 Author

👨‍💻 **Md. Azizur Rahman**  
🎓 BSc in EEE, BUET  
💡 AI • IoT • Automation Engineer  

🌐 [GitHub](https://github.com/ar-titumir)  
🔗 [LinkedIn](https://www.linkedin.com/in/ar-titumir)  
📧 Email: azizureeebuet@gmail.com  

---

**Enjoy automating your Facebook post archiving with AI-powered PDF generation!**
