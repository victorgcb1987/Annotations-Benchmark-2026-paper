from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random


def write_like_person(driver_element, text):
    for letter in text:
        driver_element.send_keys(letter)
        time.sleep(random.uniform(0.05, 0.15))


def query_timetree(species_a, species_b):
    driver = webdriver.Chrome()
    driver.get('https://timetree.org/')

    time.sleep(2)

    input_a = driver.find_element(By.XPATH, '//input[@id="taxon-a"]')
    write_like_person(input_a,species_a)

    input_b = driver.find_element(By.XPATH, '//input[@id="taxon-b"]')
    write_like_person(input_b,species_b)

    button = driver.find_element(By.XPATH, '//button[@id="pairwise-search-button1"]')
    button.click()

    time.sleep(2)

    div = driver.find_element(By.XPATH, "//div[@id='pairwiseSvg']")

    texto = div.get_attribute("innerHTML")
    list_textos = texto.split('\n')


    median = (list_textos[-10].split('>')[1]).split('<')[0]
    adjusted = (list_textos[-7].split('>')[1]).split('<')[0]

    time.sleep(1)
    driver.close()

    return {species_b: {"adjusted_time": adjusted, "median_time": median}}