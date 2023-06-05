
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = Options()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options,
    )
url = 'https://m.sports.ru/liverpool/'
browser.get(url)
try:
    for i in range(1, 6):
        browser.implicitly_wait(10)
        btn_xpath = '//button[(contains(@class,"b-tag-lenta__show-more-button")) and(contains(text(),"Показать еще"))]'
        more_btn = browser.find_element(By.XPATH, btn_xpath)
        browser.execute_script("arguments[0].click();", more_btn)
        print(f"Click #{i} done!")
finally:
    print("NOW PARSE!")
    time.sleep(20)
    print("Thanks, I'm done!")
    browser.quit()
