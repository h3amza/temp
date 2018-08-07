from __future__ import print_function
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import geopy.distance

p =  re.compile("(\[null,null,)+\-?[0-9]+\.?[0-9]*(,)+\-?[0-9]+\.?[0-9]*(\])")
q =  re.compile("[ ][0-9]{5}")

def extract(a,bit):
    if bit == 0:
        m = re.search(p,a).group(0)
        if m is not None:
            n = a[a.index(m)+len(m):a.index(m)+len(m)+100].split(',')[2].replace('\"','').replace('\\','')
            m = m.replace('[','').replace(']','').split(',')
            return n +','+str(m[2])+','+str(m[3])
        else:
            return ",,"
    else:
        m = re.search(p,a).group(0)
        if m is not None:
            n = a[a.index(m)+len(m):a.index(m)+len(m)+100].split(',')[2].replace('\"','').replace('\\','')
            m = m.replace('[','').replace(']','').split(',')
            
            x = re.search(q,a).group(0)
            if x is not None:
                return n +','+str(m[2])+','+str(m[3])+','+x.strip()
            else:
                return n +','+str(m[2])+','+str(m[3])+','
        else:
            return ",,,"

final = ""
driver = webdriver.Chrome()
driver.get('https://www.google.com/maps/search/high+school/@37.696095,-122.161714,13z')
a = driver.page_source
final += extract(a,1)
print(final)

driver.close()
