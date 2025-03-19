from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from textblob import TextBlob
import time
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Selenium WebDriver
def init_driver():
    service = Service('C:\\Windows\\chromedriver.exe')  # Update with your ChromeDriver path
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    # Disable headless mode to see the browser window
    # options.add_argument("--headless")  # Comment this line to see the browser window
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Scrape comments from YouTube
def scrape_youtube_comments(url):
    driver = init_driver()
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    # Scroll to load more comments
    for _ in range(5):  # Adjust the number of scrolls as needed
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        logging.debug("Scrolled to load more comments...")
        time.sleep(5)  # Wait longer for comments to load

    # Wait for comments section to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="comments"]'))
        )
    except Exception as e:
        logging.error(f"Error waiting for comments section to load: {e}")
        driver.quit()
        return []

    # Extract comments
    comments = []
    try:
        comment_elements = driver.find_elements(By.XPATH, '//*[@id="content-text"]')
        logging.debug(f"Found {len(comment_elements)} comments.")
        for element in comment_elements:
            comments.append(element.text)
    except Exception as e:
        logging.error(f"Error extracting comments: {e}")

    driver.quit()
    return comments

# Scrape comments from Instagram
def scrape_instagram_comments(url):
    driver = init_driver()
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    # Scroll to load more comments
    for _ in range(3):  # Adjust the number of scrolls as needed
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        logging.debug("Scrolled to load more comments...")
        time.sleep(5)

    # Wait for comments section to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//ul[@class="XQXOT"]'))
        )
    except Exception as e:
        logging.error(f"Error waiting for comments section to load: {e}")
        driver.quit()
        return []

    # Extract comments
    comments = []
    try:
        comment_elements = driver.find_elements(By.XPATH, '//span[@class="_aacl _aaco _aacu _aacx _aad7 _aade"]')
        logging.debug(f"Found {len(comment_elements)} comments.")
        for element in comment_elements:
            comments.append(element.text)
    except Exception as e:
        logging.error(f"Error extracting comments: {e}")

    driver.quit()
    return comments

# Scrape comments from Facebook
def scrape_facebook_comments(url):
    driver = init_driver()
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    # Scroll to load more comments
    for _ in range(3):  # Adjust the number of scrolls as needed
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        logging.debug("Scrolled to load more comments...")
        time.sleep(5)

    # Wait for comments section to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="du4w35lb l9j0dhe7"]'))
        )
    except Exception as e:
        logging.error(f"Error waiting for comments section to load: {e}")
        driver.quit()
        return []

    # Extract comments
    comments = []
    try:
        comment_elements = driver.find_elements(By.XPATH, '//div[@class="ecm0bbzt hv4rvrfc ihqw7lf3 dati1w0a"]')
        logging.debug(f"Found {len(comment_elements)} comments.")
        for element in comment_elements:
            comments.append(element.text)
    except Exception as e:
        logging.error(f"Error extracting comments: {e}")

    driver.quit()
    return comments

# Scrape comments from X (Twitter)
def scrape_x_comments(url):
    driver = init_driver()
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    # Scroll to load more comments
    for _ in range(3):  # Adjust the number of scrolls as needed
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        logging.debug("Scrolled to load more comments...")
        time.sleep(5)

    # Wait for comments section to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@data-testid="tweet"]'))
        )
    except Exception as e:
        logging.error(f"Error waiting for comments section to load: {e}")
        driver.quit()
        return []

    # Extract comments
    comments = []
    try:
        comment_elements = driver.find_elements(By.XPATH, '//div[@class="css-901oao r-1nao33i r-1k78y06 r-1qd0xha r-1b43r93 r-16dba41 r-ad9z0x r-bcqeeo r-qvutc0"]')
        logging.debug(f"Found {len(comment_elements)} comments.")
        for element in comment_elements:
            comments.append(element.text)
    except Exception as e:
        logging.error(f"Error extracting comments: {e}")

    driver.quit()
    return comments

# Analyze sentiment of comments using TextBlob
def analyze_sentiment(comments):
    results = {}
    for comment in comments:
        try:
            blob = TextBlob(comment)
            polarity = blob.sentiment.polarity

            if polarity > 0:
                results[comment] = "positive"
            elif polarity < 0:
                results[comment] = "negative"
            else:
                results[comment] = "neutral"
        except Exception as e:
            logging.error(f"Error analyzing sentiment for comment: {comment}. Error: {e}")
            results[comment] = "neutral"
    return results

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    platform = data.get("platform")
    url = data.get("url")
    logging.debug(f"Received request: platform={platform}, url={url}")

    if platform == "YouTube":
        comments = scrape_youtube_comments(url)
    elif platform == "Instagram":
        comments = scrape_instagram_comments(url)
    elif platform == "Facebook":
        comments = scrape_facebook_comments(url)
    elif platform == "X (Twitter)":
        comments = scrape_x_comments(url)
    else:
        return jsonify({"error": "Platform not supported yet."}), 400

    if not comments:
        return jsonify({"error": "No comments found. Please check the URL or try again later."}), 400

    results = analyze_sentiment(comments)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)