#import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By


def m_search(search_query):
    URL = 'https://mangasee123.com/search/?name=' + search_query #searches website for keyword given
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    dr = webdriver.Chrome(options=options)
    dr.get(URL)
    
    try:
        show_more_button = dr.find_element(By.XPATH, "//button[@class='btn btn-outline-primary form-control top-15 bottom-5 ng-scope']")
        while show_more_button:
            show_more_button = dr.find_element(By.XPATH, "//button[@class='btn btn-outline-primary form-control top-15 bottom-5 ng-scope']") #finds load more button
            show_more_button.click() #presses the button
    except:
        print()
    
    #---------- after expanding page, parsing through search results ----------------------#
    search_results = dr.find_element(By.XPATH, "//div[@class='col-md-8 order-md-1 order-12']") #box of search results
    manga_list = search_results.find_elements(By.XPATH, "//a[@class='SeriesName ng-binding']") #list of manga titles
    results = {}#list of manga to return
    counter = 1
    for manga in manga_list:
        results[counter] = [manga.text, manga.get_attribute('href')]
        counter += 1
        
    dr.quit()
    return results