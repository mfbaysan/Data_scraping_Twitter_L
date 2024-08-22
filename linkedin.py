import sys
import time
import pandas as pd
from typing import Tuple
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def get_credentials() -> Tuple[str, str]:
    '''get linkedin login credentials'''
    try:
        credential_file = open('linkedin_credentials.txt', 'r',
                               encoding='utf-8')
        contents = credential_file.read()
        username = contents.replace('=', ',').split(',')[1]
        password = contents.replace('=', ',').split(',')[3]
        return username, password
    except Exception:
        username = input('Enter your linkedin username: ')
        password = input('Enter your linkedin password: ')
        credential_file = open('linkedin_credentials.txt', 'w+',
                               encoding='utf-8')
        credential_file.write(f'username={username}, password={password}')
        credential_file.close()
        return username, password


def get_chrome_driver() -> webdriver.Chrome:
    '''load chrome driver'''
    options = webdriver.ChromeOptions()
    options.binary_location = '/Applications/Chromium.app/Contents/MacOS/Chromium'
    chrome_driver_binary = '/usr/local/bin/chromedriver'
    browser = webdriver.Chrome()
    return browser


def find_element(browser: webdriver.Chrome, by: str, value: str) -> str:
    '''find element of a page by id, class, etc.'''
    try:
        element = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((getattr(By, by.upper()), value)))
        return element
    except TimeoutException:
        print(f'Element {by} with value {value} is not found')
        sys.exit(1)


def login_to_linkedin(browser: webdriver.Chrome,
                      username: str, password: str) -> None:
    '''login to linkedin using credentials'''
    browser.get('https://www.linkedin.com/login?\
                fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
    username_element = find_element(browser, 'id', 'username')
    password_element = find_element(browser, 'id', 'password')
    username_element.send_keys(username)
    password_element.send_keys(password)
    password_element.submit()


def scroll_to_the_bottom(browser: webdriver.Chrome):
    '''scroll the page to the bottom to fully load the posts'''
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(3)
    screen_height = browser.execute_script(
        'return window.screen.height;')   # get the screen height of the web
    i = 1
    while True:
        browser.execute_script('window.scrollTo(0, {screen_height}*{i});'.
                               format(screen_height=screen_height, i=i))
        i += 1
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script(
            'return document.body.scrollHeight')
        if (screen_height) * i > new_height:
            break


def get_post_text(linkedin_soup: bs) -> str:
    '''get the text of the posts'''
    containers = linkedin_soup.find_all('div', class_='relative')
    post_texts = []
    if len(containers) == 0:
        return []
    # ember859 > div > div.feed-shared-update-v2__description-wrapper > div > div
    exception_count = 0
    for container in containers:
        text_box = container.find('div', attrs={'class':
                                                'update-components-text relative feed-shared-update-v2__commentary',
                                                'dir': 'ltr'})
        if text_box is None:
            exception_count += 1
            continue
        text = text_box.find('span', attrs={'dir': 'ltr'}).text
        if text is not None and text != '':
            post_texts.append(text)
    print(
        f'There are {len(containers)} containers and {len(post_texts)} posts are found with {exception_count} exceptions')
    return post_texts


def write_to_csv_file(data: pd.DataFrame, filename: str):
    '''write the data to csv file'''
    data.to_csv(filename, index=False)


if __name__ == '__main__':
    csv_file_path = '/Users/k/Desktop/Courses/idp/founders_dataset_IDP.csv'
    SCROLL_PAUSE_TIME = 0.5

    csv_file_content = pd.read_csv(csv_file_path, usecols=['person_name',
                                                           'linkedin_url'])
    username, password = get_credentials()
    browser = get_chrome_driver()
    login_to_linkedin(browser, username, password)
    broken_links = []

    url = 'https://www.linkedin.com/in/lisaputter/recent-activity/all/'
    browser.get(url)
    scroll_to_the_bottom(browser)
    linkedin_soup = bs(person_page, 'lxml')
    linkedin_soup.prettify('utf-8')


    for index, row in csv_file_content.iterrows():
        if (4200 < index or index < 4000):
            continue
        if row['person_name'] != 'Kavita Bala':
            continue
        if pd.isna(row['linkedin_url']):
            print(f'No linkedin url for {row["person_name"]}')
            continue
        linkein_url_parameters = row['linkedin_url'].split('/')
        linkedin_usrname = linkein_url_parameters[-1] if \
            linkein_url_parameters[-1] != '' else linkein_url_parameters[-2]
        url = 'http://www.linkedin.com/in/' + linkedin_usrname + \
            '/detail/recent-activity/shares/'
        browser.get(url)
        scroll_to_the_bottom(browser)
        person_page = browser.page_source
        linkedin_soup = bs(person_page, 'lxml')
        linkedin_soup.prettify('utf-8')
        with open(''.join(row['person_name'].split(' ')) + '.html',
                  'w', encoding='utf-8') as file:
            file.write(str(linkedin_soup))
        post_texts = get_post_text(linkedin_soup)
        if len(post_texts) == 0:
            alternative_url = 'http://www.linkedin.com/in/' + linkedin_usrname + \
                '/detail/recent-activity/all/'
            browser.get(alternative_url)
            scroll_to_the_bottom(browser)
            person_page = browser.page_source
            linkedin_soup = bs(person_page, 'lxml')
            linkedin_soup.prettify('utf-8')
            with open(''.join(row['person_name'].split(' ')) + '.html',
                      'w', encoding='utf-8') as file:
                file.write(str(linkedin_soup))
            post_texts = get_post_text(linkedin_soup)
            if len(post_texts) == 0:
                print(f'No posts found for {row["person_name"]}')
                broken_links.append(linkedin_usrname)
                continue
        write_to_csv_file(pd.DataFrame(post_texts),
                          ''.join(row['person_name'].split(' ')) + '.csv')

        print(f'Finished scraping {row["person_name"]} index: {index}')
    saved_broken = open('broken_linkedin.txt', 'w')
    for username in broken_links:
        file.write(username+"\n")
    saved_broken.close()