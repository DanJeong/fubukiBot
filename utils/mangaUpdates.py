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

    dr.get(URL) #gets html data from url
    last_update = dr.find_element(By.XPATH, "//a[@class='list-group-item ChapterLink ng-scope'][1]")
    last_chapter = last_update.get_attribute('href')
    dr.quit()
    return last_chapter
    