# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      "hemispheres" : hemi_images(browser)
    }

    browser.quit()

    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')

        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None   

    return news_title, news_p


def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)
  
    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:

        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

# Mars Data

def mars_facts():
    
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
        df.columns=['description', 'Mars', 'Earth']
    except BaseException:
        return None

    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    return df.to_html(classes="table", justify="center")

def hemi_images(browser):

    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    h3 = browser.find_by_css("h3")

    # List comp to turn each h3 into a string and return the first word (hemi name).
    hemi_names = [h.value.split()[0] for h in h3 if h.value != '']
    page_name = [h.value for h in h3 if h.value != '']

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    for i in range(0,4):
        
        hemispheres = {}
        
        # Navigate to hemi specific page
        
        browser.links.find_by_partial_text(hemi_names[i]).click()
        
        # Get link to "full" res image page
        
        img_url = browser.links.find_by_partial_href('full')['href']
        
        # Set title
        
        title = page_name[i]
        
        # Add to dict
        
        hemispheres['img_url'] = img_url
        hemispheres['title'] = title
        
        # Append to list
        
        hemisphere_image_urls.append(hemispheres)
        
        # Navigate to start page
        # 1 link has been followed, back once
        
        browser.back()
    
    return hemisphere_image_urls

    

#browser.quit()

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())