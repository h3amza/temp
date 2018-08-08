from __future__ import print_function
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import geopy.distance

p =  re.compile("(\[null,null,)+\-?[0-9]+\.?[0-9]*(,)+\-?[0-9]+\.?[0-9]*(\])")
q =  re.compile("['+'][0-9]{5}")


def distSub(row):
    return geopy.distance.vincenty((row['subLat_x'],row['subLong_x']),(row['compLat'],row['compLong'])).m
def compDistSchool(row):
    return geopy.distance.vincenty((row['schoolLat'],row['schoolLong']),(row['compLat'],row['compLong'])).m
def compDistGrocery(row):
    return geopy.distance.vincenty((row['groceryLat'],row['groceryLong']),(row['compLat'],row['compLong'])).m
def compDistRecreation(row):
    return geopy.distance.vincenty((row['recreationLat'],row['recreationLong']),(row['compLat'],row['compLong'])).m
def subDistSchool(row):
    return geopy.distance.vincenty((row['schoolLat'],row['schoolLong']),(row['subLat_x'],row['subLong_x'])).m
def subDistGrocery(row):
    return geopy.distance.vincenty((row['groceryLat'],row['groceryLong']),(row['subLat_x'],row['subLong_x'])).m
def subDistRecreation(row):
    return geopy.distance.vincenty((row['recreationLat'],row['recreationLong']),(row['subLat_x'],row['subLong_x'])).m

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
            
            x = re.search(q,a)
            if x is not None:
                return n +','+str(m[2])+','+str(m[3])+','+x.group(0).strip()[1:]
            else:
                return n +','+str(m[2])+','+str(m[3])+','
        else:
            return ",,,"

subj = pd.DataFrame(columns = ["guID", "subLat", "subLong", "school","schoolLat","schoolLong","zipCode","grocery",
                "groceryLat","groceryLong","recreation","recreationLat","recreationLong"])


data = pd.read_csv('000002_0', sep=",", header=None)
data.columns = ["guID", "date", "val", "subLat","subLong","rank","compLat","compLong"]

data2 = pd.concat([data['guID'],data['subLat'],data['subLong']],axis=1,keys=['guID','subLat','subLong'])
data2 =  data2.drop_duplicates('guID')

driver = webdriver.Chrome()
i = 0
for index,row in data2.iterrows():
    # find school
    final =  row['guID']+','+str(row['subLat'])+','+str(row['subLong'])+','
    driver.get('https://www.google.com/maps/search/high+school/@'+str(row['subLat'])+','+str(row['subLong'])+',13z')
    a = driver.page_source
    final += extract(a,1)+','

    # find grocery
    driver.get('https://www.google.com/maps/search/grocery/@'+str(row['subLat'])+','+str(row['subLong'])+',13z')
    a = driver.page_source
    a = driver.page_source
    final += extract(a,0)+','

    # find recreation
    driver.get('https://www.google.com/maps/search/recreation/@'+str(row['subLat'])+','+str(row['subLong'])+',13z')
    # content = driver.find_element_by_class_name('section-result-header').find_element_by_tag_name("h3").find_element_by_tag_name("span").get_attribute("innerHTML")
    a = driver.page_source
    final += extract(a,0)
    
    print(i)
    #print(final,file=out)
    final = final.split(",")
    subj.loc[len(subj)] = final
    i+=1
    if i%1000==0:
	print(i)
        subj.to_csv(r'subj'+str(i)+'.txt', header=None, index=None, sep=',', mode='a', encoding='utf-8')


combined = pd.merge(data,subj,on='guID')

distances = combined.drop('val',1).drop('rank',1). \
            drop('subLat_y',1). \
            drop('subLong_y',1)
#distances = combined

distances['sub_distSchool'] = distances.apply(subDistSchool, axis=1)
distances['sub_distGrocery'] = distances.apply(subDistGrocery, axis=1)
distances['sub_distRecreation'] = distances.apply(subDistRecreation, axis=1)

distances['comp_distSubject'] = distances.apply(distSub, axis=1)
distances['comp_distSchool'] = distances.apply(compDistSchool, axis=1)
distances['comp_distGrocery'] = distances.apply(compDistGrocery, axis=1)
distances['comp_distRecreation'] = distances.apply(compDistRecreation, axis=1)


staging = distances.drop('schoolLat',1). \
            drop('schoolLong',1).drop('groceryLat',1). \
            drop('groceryLong',1). \
            drop("recreationLat",1). \
            drop("recreationLong",1)

#staging = distances

staging.to_csv(r'000002_0_info.txt', header=None, index=None, sep=',', mode='a', encoding='utf-8')

driver.close()


#tor_process.kill()
