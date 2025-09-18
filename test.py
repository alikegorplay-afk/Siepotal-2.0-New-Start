from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Настройка опций Chrome
webdriver.Firefox()
options = webdriver.ChromeOptions()
#options.add_argument('--headless')  # Запуск в фоновом режиме (без открытия окна браузера)
# options.add_argument('--disable-blink-features=AutomationControlled')  # Скрытие автоматизации
options.add_experimental_option("excludeSwitches", ["enable-automation"])

# Автоматическая загрузка и установка ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Открываем нужную страницу
    url = "https://www.producthunt.com/leaderboard/yearly/2025"
    driver.get(url)
    
    # Ждем загрузки конкретного элемента (критически важно!)
    # Замените селектор на актуальный для вашего случая
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "styles_item__Sn_12")))  # Пример селектора
    
    # Получаем готовый HTML после выполнения JavaScript
    html = driver.page_source
    
    # Теперь можно парсить с BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Здесь ваш код для парсинга
    # Например, поиск всех элементов продукта:
    products = soup.find_all('div', class_='styles_item__Sn_12')  # Используйте правильный класс
    
    for product in products:
        # Извлечение данных из каждого продукта
        name = product.find('h3').text
        link = product.find('a')['href']
        print(f"{name}: {link}")
        
    # Или можно работать непосредственно через Selenium:
    # products = driver.find_elements(By.CLASS_NAME, 'styles_item__Sn_12')
    # for product in products:
    #     name = product.find_element(By.TAG_NAME, 'h3').text
    #     link = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
    #     print(f"{name}: {link}")

finally:
    # Всегда закрывайте браузер
    driver.quit()