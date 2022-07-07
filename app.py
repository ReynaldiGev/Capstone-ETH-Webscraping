from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url = 'https://www.coingecko.com/en/coins/ethereum/historical_data/?start_date=2020-01-01&end_date=2021-06-30' 
url_get = requests.get(url, headers = { 'User-Agent': 'Popular browser\'s user-agent', })
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs={'class':'table table-striped text-sm text-lg-normal'})
row = table.find_all('th', attrs={'class':'font-semibold text-center'})
row_length = len(row)


temp = [] #initiating a tuple
# get date
for i in range(1, row_length):
    date = table.find_all('th', attrs={'class':'font-semibold text-center'})[i].text
    temp.append(date)

vol = [] # initiating a tuple
# get volume
code = table.find_all('td', attrs={'class':'text-center'})
jump = row_length * 4
for i in range(2,jump,4):
    vol.append(code[:i][i-1].text)    

data_tuples = list(zip(temp,vol))


data_tuples = data_tuples[::-1]

#change into dataframe
df = pd.DataFrame(data_tuples, columns = ('Date','Volume'))

#insert data wrangling here
import re
df['Volume'] = df['Volume'].map(lambda x: re.sub(r'\W+', '', x))
df['Volume'] = df['Volume'].str.replace(",","")
df['Volume'] = df['Volume'].str.replace("\n","")
df['Volume'] = df['Volume'].str.strip()
df['Volume'] = df['Volume'].astype('int64')
df["Date"] = pd.to_datetime(df["Date"])
df = df.set_index('Date')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Volume"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)