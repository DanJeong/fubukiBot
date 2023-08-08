#import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time
from selenium.webdriver.common.by import By

def get_latest_chapter(URL):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    dr = webdriver.Chrome(options=options)
    
    print('running...')

    dr.get(URL) #gets html data from url
    #soup = bs(dr.page_source, 'html5lib') #parses raw html data in r
    #last_update = soup.find('div', attrs = {'class':'list-group top-10 bottom-5 ng-scope'})
    last_update = dr.find_element(By.XPATH, "//a[@class='list-group-item ChapterLink ng-scope'][1]")
    lastChapter = last_update.get_attribute('href')
    #print(f'lastChapter is: {lastChapter}')
    dr.quit()
    return lastChapter
    