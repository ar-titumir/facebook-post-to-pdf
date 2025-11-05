import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from fpdf import FPDF
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from urllib.parse import urlparse, parse_qs
import requests
import random
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def web_driver(position_x=1600, position_y=300):
    options = webdriver.ChromeOptions()
    # Set Chrome options to block images, CSS, fonts, etc.
    chrome_prefs = {
        # "profile.managed_default_content_settings.images": 2,
        # "profile.managed_default_content_settings.stylesheets": 2,
        # "profile.managed_default_content_settings.fonts": 2,
        # "profile.managed_default_content_settings.plugins": 2,
        # "profile.managed_default_content_settings.popups": 2,
        # "profile.managed_default_content_settings.geolocation": 2,
        # "profile.managed_default_content_settings.notifications": 2,
    }
    options.add_experimental_option("prefs", chrome_prefs)
    # options.add_argument("--headless")  # Run headless if you don't need a visible browser
    # options.add_argument('--start-maximized')  # maximized window
    # Set window size: width=800px, height=600px
    options.add_argument("--window-size=800,600")
    # Set window position: x=100px from left, y=50px from top
    options.add_argument(f"--window-position={position_x},{position_y}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Initialize driver
    # return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


class NextAndSave():
    def __init__(self, driv, url, image_dir="post_images", pdf_dir = None, pdf_file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".pdf"):
        self.page1_url = url
        self.current_url = url
        self.driver = driv
        self.delay_factor = 1
        self.img_dir = image_dir
        os.makedirs(self.img_dir, exist_ok=True)
        pdf_dir = pdf_dir if pdf_dir else "pdf_files"
        os.makedirs(pdf_dir, exist_ok=True)
        self.pdf_dir = os.path.join(pdf_dir, pdf_file_name)
        self.page_counter = 0
        self.page_ids = {}
        self.driver.get(self.current_url)
        time.sleep(3)

    def monitor_download(self, futures_list, stop_event, print_event):
        while not stop_event.is_set():
            if print_event.is_set():
                print_event.clear()
                total = len(futures_list)
                done = sum(1 for f, _ in futures_list if f.done())
                running = sum(1 for f, _ in futures_list if f.running())
                print(f"[monitor] total={total} running={running} done={done}")
                # optionally print first few completed results
            time.sleep(0.02)

    def next_n_save(self):
        executor = ThreadPoolExecutor(max_workers=6)
        futures = []  # list of (future, link)
        stop_evt = threading.Event()
        print_evt = threading.Event()
        mon = threading.Thread(target=self.monitor_download, args=(futures, stop_evt, print_evt), daemon=True)
        mon.start()

        try:
            while True:
                self.current_url = self.driver.current_url
                query = parse_qs(urlparse(self.current_url).query)
                page_id = query.get('fbid', [None])[0]
                if page_id in self.page_ids:
                    print("No new pages found. Exiting.")
                    break
                self.page_ids[page_id] = True
                self.page_counter += 1

                # divs = self.driver.find_elements(By.XPATH, "//div[starts-with(@style, 'transform:translate')]")
                divs = self.driver.find_elements(By.XPATH, "//img[@data-visualcompletion]")
                if len(divs) == 0:
                    print(f"No image tags found on the page. Page link: {self.current_url}")
                    continue
                src = [div.get_attribute("src") for div in divs if div.get_attribute("src")] # and page_id in div.get_attribute("src")]
                
                if len(src) == 0:
                    print(f"No image link found. Page link: {self.current_url}")
                    continue
                elif len(src) > 1:
                    print(f"Multiple image divs found on the page. Count: {len(src)} Page link: {self.current_url}")
                src = src[0]
# 
                # run download using threading
                fut = executor.submit(self.download_image, src, f"{self.page_counter}")
                # print("Submitted download task for", src)
                futures.append((fut, self.current_url))
                print_evt.set()
                # Click the 'Next' button
                try:
                    # Wait until the element is clickable (max 10 seconds)
                    next_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Next photo"]'))
                    )
                    
                    # Click the element
                    next_button.click()
                    # print("✅ Clicked on 'Next photo' button!")
                    time.sleep(1 * self.delay_factor)  # wait for page to load

                except Exception as e:
                    print("❌ Error:", e)

        except Exception as e:
            print("Error during next_n_save:", e)

        finally:
            # wait for all to finish
            executor.shutdown(wait=True)
            stop_evt.set()
            mon.join(timeout=2)
            print("All tasks completed.")
            # collect results
            results = []
            for f, link in futures:
                try:
                    results.append((link, f.result()))
                except Exception as e:
                    results.append((link, f"ERR: {e}"))
            print("Results:", results)

    def download_image(self, url, counter):
        # print("I love programming")
        filename = os.path.join(self.img_dir, f"{int(counter):03d}.jpg")
        print("downloading", url, "to", filename)
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            with open(filename, "wb") as f:
                f.write(r.content)
            print("saved", filename)
        except Exception as e:
            print("failed", url, e)

    def make_pdf(self, pdf_dir = None):
        if not pdf_dir:
            pdf_dir = self.pdf_dir
        print(f"Creating PDF from {self.page_counter} images...")
        if self.page_counter > 0:
            pdf = FPDF(unit="pt")  # Use points as unit for precise sizing
            for i in range(1, self.page_counter + 1):
                img_path = os.path.join(self.img_dir, f"{i:03d}.jpg")
                if os.path.exists(img_path):
                    image = Image.open(img_path)
                    w, h = image.size  # size in pixels

                    # Create a page with the same size as the image
                    pdf.add_page(orientation='P', format=(w, h))
                    pdf.image(img_path, 0, 0, w, h)  # keep actual image size

            pdf.output(pdf_dir)
            print(f"📄 PDF created successfully: {pdf_dir}")
        else:
            print("No images saved. PDF not created.")



class AccessPosts():
    def __init__(self, post_link="https://www.facebook.com/"):
        # self.driver = web_driver()
        self.delay_factor = 1
        # self.driver_init(link=post_link)
    
    def driver_init(self, link="https://www.facebook.com/"):
        self.base_url = link
        self.image1_url = None
        try:
            print(f"Driver alive!  Current url: {self.driver.current_url}")
        except Exception:
            print("Creating new driver")
            self.driver = web_driver()
            time.sleep(0.3)
            self.add_cookies()
            time.sleep(0.3)
        self.driver.get(link)
        time.sleep(2)

    def create_node(self, pdf_dir=None, pdf_file_name_=None):
        if not pdf_file_name_ or not pdf_file_name_.endswith(".pdf"):
            pdf_file_name_ = self.get_pdf_name()
        else:
            print(f"Using file name: {pdf_file_name_}")

        self.next_and_save = NextAndSave(self.driver, self.get_image1_url(), pdf_dir=pdf_dir, pdf_file_name=pdf_file_name_)
        self.next_and_save.next_n_save()
        self.next_and_save.make_pdf()

    def add_cookies(self, cookies_file="fb1.txt"):
        self.driver.get("https://www.facebook.com")
        time.sleep(self.delay_factor*0.1)  # wait for page load
        with open(cookies_file, "r") as file:
            cookies = json.load(file)
        # Add cookies
        for cookie in cookies:
            # Remove keys Selenium does not accept
            cookie.pop("sameSite", None)
            cookie.pop("storeId", None)
            cookie.pop("hostOnly", None)
            cookie.pop("session", None)
            self.driver.add_cookie(cookie)
        self.driver.refresh()

    def get_caption(self):
        cap = self.driver.find_elements(By.XPATH, "//div[@data-ad-preview='message' and @data-ad-comet-preview='message']")
        cap_texts = [c.text for c in cap if c.text]
        print("Captions found:", cap_texts)
        return cap_texts

    def get_image1_url(self):
        # divs = self.driver.find_elements(By.XPATH, "//div[contains(@style, 'bottom') and contains(@style, 'calc')]")
        # if divs:
        #     style = divs[0].find_elements(By.TAG_NAME, "a")
        #     urls = [a.get_attribute("href") for a in style if a.get_attribute("href") and "fbid" in a.get_attribute("href")]
        #     if len(urls) > 1:
        #         print("More that 1 Image URLs found:", urls)
        #     elif len(urls) == 0:
        #         print("Failed to get image 1 link")
        #     try:
        #         self.image1_url = urls[0]
        #         return self.image1_url
        #     except Exception as e:
        #         print("Error retrieving image URL:", e)
        #     finally:
        #         return None
        # print("No image divs found!")
        # return None
        divs = self.driver.find_elements(By.TAG_NAME, "a")
        a = ([x.get_attribute("href") for x in divs if x.get_attribute("href")])
        a = [x for x in a if "/photo" in x and "set=pcb" in x and "fbid=" in x]
        if len(a) == 0:
            class NoImageLinkError(Exception):
                pass
            raise NoImageLinkError("No image link found")
        
        print(f"{len(a)} image links found")
        for x in a:
            print(x)
        self.image1_url = a[0]
        return a[0]
    
    
    def get_pdf_name(self):
        cap = self.get_caption()[-1].replace("#", " ")
        prompt = """
        this is a the caption of a facebook post. This post contains an images of 
        relavant topics. i have downloaded the images. now making a pdf file from these images.
        give me a suitable concise file name for this pdf file.
        your response should be: <file_name>.pdf
        no other text.
        """
        try:
            r = requests.get(f"http://127.0.0.1:8000/api/local?prompt={cap+prompt}")
            pdf_file_name = (r.json())["result"]["response"]["response"]
            print(f"AI generated file name: {pdf_file_name}")
            # return pdf_file_name
        except:
            pdf_file_name = None
        if pdf_file_name is None or not pdf_file_name.endswith(".pdf"):
            pdf_file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".pdf"
            print(f"Using file name: {pdf_file_name}")
        return pdf_file_name

    def close(self):
        self.driver.quit()

ob = AccessPosts(post_link="https://www.facebook.com/")

def run_from_txt_file(file_path, pdf_file_folder=None):
    input_links = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                input_links.append(line)
        input_links = list(set(input_links))
    except Exception as e:
        print(f"Dir({file_path}) can not be opened! Error: {e}")
        return f"Dir can not be opened! "

    output_links = read_downloaded_list()

    downloaded_any = False
    for link in input_links:
        link = link.replace("\n", "")
        link = link.rstrip("/")
        if link not in output_links and "https://www.facebook.com" in link:
            ob.driver_init()
            ob.base_url = link
            ob.driver.get(ob.base_url)
            time.sleep(2)
            ob.create_node(pdf_dir=pdf_file_folder)
            append_output_file(link)
            downloaded_any = True
        else:
            print("Link already exist in downloaded list!")

    return "All PDF generated!" if downloaded_any else "All posts accessed previously"
    # ob.close()
    # del ob


def run_a_single_link(link, pdf_file_folder=None, pdf_file_name=None):

    if "https://www.facebook.com/" not in link:
        print(f"Link not valid: {link}")
        return "Please enter a valid facebook link"
    
    output_links = read_downloaded_list()

    link = link.replace("\n", "")
    link = link.rstrip("/")
    # print(f"link: {link}")
    if link in output_links:
        print("Link already exist in downloaded list!") 
        return "Link already exist in accessed post list!"  

    print("Driver initialization ")
    ob.driver_init()

    ob.base_url = link
    print(f"Accessing targeted post. Link: {link}")
    ob.driver.get(ob.base_url)
    time.sleep(4)
    ob.create_node(pdf_dir=pdf_file_folder, pdf_file_name_=pdf_file_name)
    append_output_file(link)
    # ob.driver.refresh()
    # ob.driver.get("https://www.facebook.com/")
    print(f"Downloaded: {link}")
    return "Downloaded All Images as PDF!"
        
def read_downloaded_list():
    if not os.path.exists("downloaded.txt"):
        with open("downloaded.txt", "w") as f:
            pass   # creates an empty file

    output_links = []
    with open("downloaded.txt", "r") as f:
        for line in f:
            line = line.replace("\n", "")
            line = line.rstrip("/")
            if "https://www.facebook.com" in line:
                output_links.append(line)
                # print(line)
        print(f"{len(output_links)} links found")

    return output_links

def append_output_file(link):
    print("Trying to append to dowloaded.txt")
    with open("downloaded.txt", "a") as f:
        print(f"Link Added in Downloaded list: {link}")
        f.write("\n"+link)
