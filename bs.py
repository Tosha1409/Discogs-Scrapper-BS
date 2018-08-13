from bs4 import BeautifulSoup
import urllib.request
import csv
import re
import time

#settings (file with list of items, folder for pictures)
picturesfolder="pictures/"
csvfile='items.csv'

#starting URL (first page of seller that you want to parse)
url = "https://www.discogs.com/seller/swampmusiccom/profile?sort=artist%2Casc&limit=25"

#dowloading file and creating soup
html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser')

#parsing link to next page if it is exits(not really used since it is ended that scrapping goes very slowly because server pretty fastly starting reject requests)
if not (soup.find('a', class_='pagination_next')) is None : page_next= "https://www.discogs.com"+soup.find('a', class_='pagination_next').get('href')
	
#parsing titles
titles=soup.find_all('a', class_='item_description_title')

#parsing labels information
labels=soup.find_all('p', class_='hide_mobile label_and_cat')

#parsing information about items conditions
conditions=soup.find_all('p', class_='item_condition')

#parsing prices
prices=soup.find_all('span', class_='price')

#storing all information
items = []

#persing info from page
for line in titles:
	item = {}
	timer = 5
	item['link'] = "https://www.discogs.com"+line.get('href')
	item['artist'], line = line.text.split(' - ', 1)
	item['title'], line = line.rsplit('(', 1)
	item['form'] = line.split(')', 1)[0]
        #Parsing picture
	item['picture'] = None
	while item['picture'] is None:
		time.sleep(timer)
		try:
			#check more carefully
			html2 = urllib.request.urlopen(item['link']).read()
			soup2 = BeautifulSoup(html2, 'html.parser')
			tmp=soup2.find('span', class_='thumbnail_center')
			item['picturelink']=tmp.find('img').get('src')
			item['picture'] = (item['picturelink'].rsplit('/',1))[1].split('.',1)[0]+'.jpg'
			print ('Picture ' + item['picture']+ ' found') 
		except:
			timer = timer * 2
			print ('finding picture failed!')			 
	items.append(item)

	#downloading picture
	Trigger = None
	while Trigger is None:
		time.sleep(timer)
		try:
			urllib.request.urlretrieve(item['picturelink'], picturesfolder+item['picture'])
			Trigger = False
		except:
			timer = timer * 2
			print ('saving picture error. Trying once again')

#parsing labels information (actually it takes only one if there is few), and it walks in html try more for learning purposes	
m=0
for label in labels:
	for tmp in label.children:
		try:
			if tmp.get('href') is not None :
				items[m]['label']=tmp.text
				items[m]['labellink']=tmp.get('href')		
		except:
			pass
	items[m]['catnumber']=label.find('span', class_='item_catno').text
	items[m]['price']=prices[m].text
	m += 1
	
#parsing condition (sleeve and media)
m=0
for condition in conditions:
	items[m]['scondition']="None"
	items[m]['mcondition']="None"
	try:
		items[m]['scondition']=condition.find('span', class_='item_sleeve_condition').text
		items[m]['mcondition']=condition.find('i', class_='icon icon-info-circle muted media-condition-tooltip').get('data-condition')
	except:
		pass
	m += 1

#making CSV file
writer = csv.writer(open(csvfile, 'w'), delimiter ='\t', quotechar=None)

#forming first line for csv
writer.writerow(
	('artist', 'title', 'form', 'catnumber', 'link', 'label', 'labellink', 'picture', 'picturelink', 'scondition', 'mcondition', 'price')
	)

#parsing rest of rows to csv
for item in items:
	writer.writerow(
		(item['artist'], (item['title'].encode('ascii','ignore')).decode(), item['form'], item['catnumber'], item['link'], item['label'], item['labellink'], item['picture'], item['picturelink'], item['scondition'], item['mcondition'], (item['price'].encode('ascii','ignore')).decode())
		)