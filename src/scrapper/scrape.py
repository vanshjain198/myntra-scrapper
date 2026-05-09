# Importing selenium to automate browser
from selenium import webdriver

# Used to find elements on webpage
from selenium.webdriver.common.by import By

# Importing custom exception for better error handling
from src.exception import CustomException

# BeautifulSoup is used to extract data from HTML
from bs4 import BeautifulSoup as bs

# Pandas is used to store data in table format
import pandas as pd

# os and sys used for system operations and error handling
import os, sys

# time is used to pause execution
import time

# Used to set chrome browser options
from selenium.webdriver.chrome.options import Options

# quote converts text into URL format
# urljoin joins base URL with relative URL
from urllib.parse import quote, urljoin


# Main class for scraping Myntra reviews
class ScrapeReviews:

    # Constructor runs automatically when object is created
    def __init__(self, product_name: str, no_of_products: int):

        # Setting chrome options
        options = Options()

        # Launching chrome browser
        self.driver = webdriver.Chrome(options=options)

        # Product name entered by user
        self.product_name = product_name

        # Number of products to scrape
        self.no_of_products = no_of_products


    # Function to collect product URLs from Myntra
    def scrape_product_urls(self, product_name):

        try:
            # Replacing spaces with -
            search_string = product_name.replace(" ", "-")

            # Encoding search query for URL
            encoded_query = quote(search_string)

            # Opening Myntra search page
            self.driver.get(
                f"https://www.myntra.com/{search_string}?rawQuery={encoded_query}"
            )

            # Getting page source
            myntra_text = self.driver.page_source

            # Parsing HTML using BeautifulSoup
            myntra_html = bs(myntra_text, "html.parser")

            # Finding product section
            pclass = myntra_html.findAll("ul", {"class": "results-base"})

            product_urls = []

            # Extracting all product links
            for i in pclass:
                href = i.find_all("a", href=True)

                for product_no in range(len(href)):
                    t = href[product_no]["href"]
                    product_urls.append(t)

            return product_urls

        except Exception as e:
            raise CustomException(e, sys)


    # Function to extract product details and review page link
    def extract_reviews(self, product_link):

        try:
            # Creating full product URL
            productLink = urljoin("https://www.myntra.com", product_link)

            # Opening product page
            self.driver.get(productLink)

            # Getting page source
            prodRes = self.driver.page_source

            # Parsing HTML
            prodRes_html = bs(prodRes, "html.parser")

            # Getting product title
            title_h = prodRes_html.findAll("title")
            self.product_title = title_h[0].text

            # Extracting overall rating
            overallRating = prodRes_html.findAll(
                "div",
                {"class": "index-overallRating"}
            )

            for i in overallRating:
                self.product_rating_value = i.find("div").text

            # Extracting price
            price = prodRes_html.findAll(
                "span",
                {"class": "pdp-price"}
            )

            for i in price:
                self.product_price = i.text

            # Getting review page link
            product_reviews = prodRes_html.find(
                "a",
                {"class": "detailed-reviews-allReviews"}
            )

            # If no reviews found
            if not product_reviews:
                return None

            return product_reviews

        except Exception as e:
            raise CustomException(e, sys)


    # Function to scroll page and load all reviews
    def scroll_to_load_reviews(self):

        # Setting browser window size
        self.driver.set_window_size(1920, 1080)

        # Getting initial page height
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )

        while True:

            # Scroll down
            self.driver.execute_script("window.scrollBy(0, 1000);")

            # Wait for page loading
            time.sleep(3)

            # Get new height
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )

            # Stop if page fully loaded
            if new_height == last_height:
                break

            last_height = new_height


    # Function to extract user reviews
    def extract_products(self, product_reviews, product_url):

        try:
            # Review page link
            t2 = product_reviews["href"]

            Review_link = urljoin("https://www.myntra.com", t2)

            # Product page link
            Product_link = urljoin("https://www.myntra.com", product_url)

            # Open review page
            self.driver.get(Review_link)

            # Load all reviews
            self.scroll_to_load_reviews()

            # Get page source
            review_page = self.driver.page_source

            # Parse HTML
            review_html = bs(review_page, "html.parser")

            # Extract review containers
            review = review_html.findAll(
                "div",
                {"class": "detailed-reviews-userReviewsContainer"}
            )

            # Extract rating, comment and username
            for i in review:

                user_rating = i.findAll(
                    "div",
                    {"class": "user-review-main user-review-showRating"}
                )

                user_comment = i.findAll(
                    "div",
                    {"class": "user-review-reviewTextWrapper"}
                )

                user_name = i.findAll(
                    "div",
                    {"class": "user-review-left"}
                )

            reviews = []

            # Maximum 5 reviews
            max_reviews = min(5, len(user_rating))

            for i in range(max_reviews):

                # Getting user rating
                try:
                    rating = user_rating[i].find(
                        "span",
                        class_="user-review-starRating"
                    ).get_text().strip()

                except:
                    rating = "No rating Given"

                # Getting user comment
                try:
                    comment = user_comment[i].text

                except:
                    comment = "No comment Given"

                # Getting username
                try:
                    name = user_name[i].find("span").text

                except:
                    name = "No Name given"

                # Getting review date
                try:
                    date = user_name[i].find_all("span")[1].text

                except:
                    date = "No Date given"

                # Storing all review data in dictionary
                mydict = {

                    "Product Name": self.product_title,

                    "Product Link": Product_link,

                    "Over_All_Rating": self.product_rating_value,

                    "Price": self.product_price,

                    "Date": date,

                    "Rating": rating,

                    "Name": name,

                    "Comment": comment,
                }

                reviews.append(mydict)

            # Convert reviews into dataframe
            review_data = pd.DataFrame(
                reviews,
                columns=[
                    "Product Name",
                    "Product Link",
                    "Over_All_Rating",
                    "Price",
                    "Date",
                    "Rating",
                    "Name",
                    "Comment",
                ],
            )

            return review_data

        except Exception as e:
            raise CustomException(e, sys)


    # Main function to combine everything
    def get_review_data(self) -> pd.DataFrame:

        try:
            # Get all product URLs
            product_urls = self.scrape_product_urls(
                product_name=self.product_name
            )

            # Remove duplicate URLs
            product_urls = list(dict.fromkeys(product_urls))

            product_details = []

            scraped_count = 0

            # Loop through products
            for product_url in product_urls:

                # Stop when required products scraped
                if scraped_count >= self.no_of_products:
                    break

                # Extract review section
                review = self.extract_reviews(product_url)

                if review:

                    # Extract complete review data
                    product_detail = self.extract_products(
                        review,
                        product_url
                    )

                    product_details.append(product_detail)

                    scraped_count += 1

            # Close browser
            self.driver.quit()

            # Return empty dataframe if no data
            if not product_details:
                return pd.DataFrame()

            # Combine all dataframes
            data = pd.concat(product_details, axis=0)

            # Save data into CSV file
            data.to_csv("data.csv", index=False)

            return data

        except Exception as e:

            # Close browser if error occurs
            self.driver.quit()

            raise CustomException(e, sys)