from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set logging for debugging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

@app.route('/scrape', methods=['GET'])
def scrape_jobs():
    """Scrape Indeed job postings based on keyword and location."""
    keyword = request.args.get('keyword', 'Software Engineer')
    location = request.args.get('location', 'United States')

    # Format the Indeed URL
    url = f"https://www.indeed.com/jobs?q={keyword.replace(' ', '+')}&l={location.replace(' ', '+')}"

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode
    options.add_argument('--disable-gpu')  # Disable GPU rendering
    options.add_argument('--no-sandbox')  # Bypass OS security model
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        app.logger.debug(f"Fetching URL: {url}")
        driver.get(url)

        # Find job postings
        job_cards = driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')
        jobs = []

        for card in job_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, 'h2.jobTitle').text
                company = card.find_element(By.CSS_SELECTOR, 'span.companyName').text
                location = card.find_element(By.CSS_SELECTOR, 'div.companyLocation').text
                jobs.append({"title": title, "company": company, "location": location})
            except Exception as e:
                app.logger.warning(f"Error extracting job details: {e}")

        driver.quit()
        return jsonify(jobs)

    except Exception as e:
        driver.quit()
        app.logger.error(f"Error during scraping: {e}")
        return jsonify({"error": "An internal error occurred while scraping jobs."}), 500

if __name__ == '__main__':
    app.run(debug=True)
