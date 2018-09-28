from __future__ import print_function
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sys
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import ElementNotSelectableException
from selenium.common.exceptions import InvalidSelectorException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import SessionNotFoundException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException


from pyvirtualdisplay import Display
import pandas as pd
import time
import geopy.distance


display = Display(visible=0,size=(800,800))
display.start()

z =  re.compile('display_zip(.*)</div>')
s =  re.compile('display_state(.*)</div>')
add = re.compile('display_address(.*)</div>')
c = re.compile('display_city(.*)</div>')

def distSub(row):
    return geopy.distance.vincenty((row['subLat_x'],row['subLong_x']),(row['compLat'],row['compLong'])).m


def extract(a):
    zipcode = re.search(z,a)
    if zipcode is not None:
        zipcode = zipcode.group(0)
    else:
        zipcode = ""
    state = re.search(s,a)
    if state is not None:
        state = state.group(0)
    else:
        state = ""
    address = re.search(add,a)
    if address is not None:
        address = address.group(0)
    else:
        address = ""
    city = re.search(c,a)
    if city is not None:
        city = city.group(0)
    else:
        city = ""
    return zipcode[13:-6]+","+state[15:-6]+","+address[17:-6].replace(',',' ')+","+city[14:-6]


subj = pd.DataFrame(columns = ["guID", "subLat", "subLong", "zipcode","state","address","city"])

data = pd.read_csv(sys.argv[1], sep=",", header=None)
data.columns = ["guID", "date", "val", "subLat","subLong","rank","compLat","compLong"]

data2 = pd.concat([data['guID'],data['subLat'],data['subLong']],axis=1,keys=['guID','subLat','subLong'])
data2 =  data2.drop_duplicates('guID')
print(len(data2))

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-setuid-sandbox")
options.add_argument("--disable-extensions")
options.add_argument("disable-infobars")
driver = webdriver.Chrome(chrome_options=options)
i = 0
skipped = 0
for index,row in data2.iterrows():
    link = 'https://www.mapdevelopers.com/what-is-my-zip-code.php?address='+str(row['subLat'])+'%2C'+str(row['subLong'])
    final =  str(row['guID'])+','+str(row['subLat'])+','+str(row['subLong'])+','
    # place holder
    try:
        driver.get(link)
        time.sleep(2)
        a = driver.page_source
        final += extract(a)
        print(i)
        #print(final)
        #placeholder
        final = final.split(",")
        subj.loc[len(subj)] = final
        i+=1
        if i%500==0:
            print(i)
            subj.to_csv(r'subj'+str(i)+'.txt', header=None, index=None, sep=',', mode='a', encoding='utf-8')
    except ElementNotVisibleException:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)
    except ElementNotSelectableException:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)
    except InvalidSelectorException:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)
    except NoSuchElementException:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)
    except NoSuchFrameException:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)
    except NoAlertPresentException:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)
    except NoSuchWindowException:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)
    except StaleElementReferenceException:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)
    except SessionNotFoundException:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)
    except TimeoutException:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)
    except WebDriverException:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)
    except Exception:
        i+=1
        print("resetting driver, skipped "+str(skipped))
        driver.close()
        time.sleep(2)
        driver = webdriver.Chrome(chrome_options=options)

combined = pd.merge(data,subj,on='guID')
distances = combined.drop('subLat_y',1). \
            drop('subLong_y',1)
distances['distance'] = distances.apply(distSub, axis=1)

distances.to_csv('1_'+sys.argv[1]+'.txt', header=None, index=None, sep=',', mode='a', encoding='utf-8')



driver.close()


#tor_process.kill()
