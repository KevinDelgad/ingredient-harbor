from flask import Flask, request, jsonify
from selenium import webdriver
import json
import re
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests as bs4Requests

app = Flask(__name__)

def staticScrape(site, key, listType):
    page_source_static = BeautifulSoup(bs4Requests.get(site).text, 'lxml')
    found = page_source_static.find_all(listType, key)
    ingredientList = []
    dividedIngredientList = []
    for ingredient in found:
        if(ingredient.text != 'Deselect All' and ingredient.text != 'Select All'):
            ingredientList.append(ingredient.text)

    for ingredient in ingredientList:
        processedIngredient = ingredient.replace('\n', '')
        ingredientSplit = re.match("^([\d/]+ [a-zA-Z]+[.]?) (.+)$", processedIngredient)
        if(ingredientSplit):
            dividedIngredientList.append([ingredientSplit.group(1), ingredientSplit.group(2)])
        else:
            dividedIngredientList.append(processedIngredient)
    return(dividedIngredientList)

def dynamicScrape(site, key, listType):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(site)
    page_source = driver.page_source
    driver.close()

    page_source_dynamic = BeautifulSoup(page_source, "lxml")
    found = page_source_dynamic.find_all(listType, key)
    ingredientList = []
    dividedIngredientList = []
    for ingredient in found:
        if(ingredient.text != 'Deselect All' and ingredient.text != 'Select All'):
            ingredientList.append(ingredient.text)

    for ingredient in ingredientList:
        processedIngredient = ingredient.replace('\n', '')
        ingredientSplit = re.match("^([\d/]+ [a-zA-Z]+) (.+)$", processedIngredient)
        if(ingredientSplit):
            dividedIngredientList.append([ingredientSplit.group(1), ingredientSplit.group(2)])
        else:
            dividedIngredientList.append(processedIngredient)
    return(dividedIngredientList)


def getSiteName(site):
    regexPattern = re.search('[.][a-zA-z]+[.]', site)
    return regexPattern.group(0).strip(".")

def checkStatic(site, key):
    page_source_static = BeautifulSoup(bs4Requests.get(site).text, 'lxml')
    found = page_source_static.find_all("li", key)
    if(found):
        return True
    return False

def checkValidMeasurements(inputtedList):
    valid_measurements = [
        "teaspoon",
        "tablespoon",
        "cup",
        "pint",
        "quart",
        "gallon",
        "tbsp.",
        "tbsp",
        "tsp",
        "tsp.",
        "qrt.",
        "qrt"

    ]
    
    if(inputtedList.split()[1] in valid_measurements):
        return True
    return False

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/scrapeIngredients", methods=['GET', 'POST'])
def test():
    formatfile = open('format.json')
    formatData = json.load(formatfile)
    formatfile.close()
    site_name = getSiteName(request.args.get('website'))
    site_link = request.args.get('website')
    key = formatData['singleKey'][site_name]["ingredientListKey"]
    listType = formatData['singleKey'][site_name]["ingredientListType"]
    if(checkStatic(site_link, key)):
        return(staticScrape(site_link, key, listType))
    else:
        return(dynamicScrape(site_link, key, listType))

    

    