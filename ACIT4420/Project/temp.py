from selenium import webdriver

op = webdriver.ChromeOptions()
op.add_argument('--headless')
op.add_argument("--log-level=3")
driver = webdriver.Chrome(options=op)



driver.get("https://www.nrk.no")

elems = driver.find_elements_by_xpath("//a[@href]")

for elem in elems:
    print(elem.get_attribute("href"))

print(len(elems))
