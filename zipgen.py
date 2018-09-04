from __future__ import print_function
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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

data = pd.read_csv('0_1', sep=",", header=None)
data.columns = ["guID", "date", "val", "subLat","subLong","rank","compLat","compLong"]

data2 = pd.concat([data['guID'],data['subLat'],data['subLong']],axis=1,keys=['guID','subLat','subLong'])
data2 =  data2.drop_duplicates('guID')
print(len(data2))

options = Options()
#options.add_argument("--no-sandbox")
#options.add_argument("--disable-setuid-sandbox")

driver = webdriver.Chrome(chrome_options=options)
i = 0
for index,row in data2.iterrows():
    # find school
    final =  str(row['guID'])+','+str(row['subLat'])+','+str(row['subLong'])+','
    driver.get('https://www.mapdevelopers.com/what-is-my-zip-code.php?address='+str(row['subLat'])+'%2C'+str(row['subLong']))
    time.sleep(2)
    a = driver.page_source
    final += extract(a)
    
    print(i)
    print(final)
    final = final.split(",")
    subj.loc[len(subj)] = final
    i+=1
    if i%1000==0:
        print(i)
        subj.to_csv(r'subj'+str(i)+'.txt', header=None, index=None, sep=',', mode='a', encoding='utf-8')



combined = pd.merge(data,subj,on='guID')
distances = combined.drop('subLat_y',1). \
            drop('subLong_y',1)
distances['distance'] = distances.apply(distSub, axis=1)

distances.to_csv(r'0_1_info.txt', header=None, index=None, sep=',', mode='a', encoding='utf-8')



driver.close()


#tor_process.kill()
