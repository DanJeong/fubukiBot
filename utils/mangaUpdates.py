#import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time


def main():
    URL = 'https://mangasee123.com/manga/Weak-Hero'  #url of manga to check
    

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    dr = webdriver.Chrome(options=options)
    
    print('running...')

    dr.get(URL) #gets html data from url
    soup = bs(dr.page_source, 'html5lib') #parses raw html data in r
    last_update = soup.find('div', attrs = {'class':'list-group top-10 bottom-5 ng-scope'})

    while True:
        time.sleep(600)
        dr.get(URL)
        soup = bs(dr.page_source, 'html5lib')
        curr_update = soup.find('div', attrs = {'class':'list-group top-10 bottom-5 ng-scope'})

        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)

        if last_update == curr_update:
            print('no new update. Current time: ' + current_time)
            last_update = curr_update
            continue
        else:
            print('new chapter available! Current time: ' + current_time)
            break
        
    dr.quit()

if __name__ == '__main__': main()