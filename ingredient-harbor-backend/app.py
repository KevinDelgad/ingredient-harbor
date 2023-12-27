from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/test", methods=['GET', 'POST'])
def test():
    site_link = request.args.get('website')
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(site_link)
    page_source = driver.page_source
    driver.close()

    soup = BeautifulSoup(page_source, 'lxml')
    links = soup.find_all('span', {'class': 'o-Ingredients__a-Ingredient--CheckboxLabel'})
    ingredientList = []
    dividedIngredientList = []
    for elems in links:
        if(elems.text != 'Deselect All' and elems.text != 'Select All'):
            ingredientList.append(elems.text)

    return(ingredientList)