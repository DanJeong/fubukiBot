#import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time


def m_search(search_query):
    #search_query = 'fate'
    #search_query = input('manga to search for: ')
    URL = 'https://mangasee123.com/search/?name=' + search_query #searches website for keyword given
    

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    dr = webdriver.Chrome(options=options)
    
    print('running...')
    dr.get(URL)
    
    #testy = dr.find_element(By.XPATH, "//button[@class='btn btn-outline-primary form-control top-15 bottom-5 ng-scope']")
    #print(testy)
    #print('before while loop')

    #dr.find_element(By.XPATH, "//button[@class='btn btn-outline-primary form-control top-15 bottom-5 ng-scope']")
    #while WebDriverWait(dr, 3).until(lambda d: d.find_element(By.XPATH, "//button[@class='btn btn-outline-primary form-control top-15 bottom-5 ng-scope']")):
    try:
        showMoreButton = dr.find_element(By.XPATH, "//button[@class='btn btn-outline-primary form-control top-15 bottom-5 ng-scope']")
        while showMoreButton:
            showMoreButton = dr.find_element(By.XPATH, "//button[@class='btn btn-outline-primary form-control top-15 bottom-5 ng-scope']") #finds load more button
            showMoreButton.click() #presses the button
            print('button pressed')
    except:
        print("no more button")
    
    #dr.get(URL) #gets html data from url
    
    #---------- after expanding page, parsing through search results ----------------------#
    search_results = dr.find_element(By.XPATH, "//div[@class='col-md-8 order-md-1 order-12']") #box of search results
    manga_list = search_results.find_elements(By.XPATH, "//a[@class='SeriesName ng-binding']") #list of manga titles
    print(f'results found: {len(manga_list)}')
    results = {}#list of manga to return
    counter = 1
    for manga in manga_list:#prints out all manga titles
        results[counter] = [manga.text, manga.get_attribute('href')]
        counter += 1

    #---------------------parse through search results with bs (only works on first page of results)----------------#
    '''soup = bs(dr.page_source, 'html5lib') #parses raw html data in r
    search_results = soup.find('div', attrs = {'class':'ng-scope', 'ng-if':'vm.Warning == \'\''}) #gets box where search results are stored
    manga_list = search_results.find_all('div', attrs = {'class':'top-15 ng-scope'}) #gets list of manga in search result
    #print(manga_list)
    for manga in manga_list: #for each manga, print title
        container = manga.find('a', attrs = {'class':'SeriesName ng-binding'})
        title = container.get_text()
        print(title)'''
        
    dr.quit()
    return results
#if __name__ == '__main__': main()