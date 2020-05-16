#htbot V1.3 - released 15 jul 2019
#@dvd14986 - dvd14986@gmail.com

import sys
import requests # --> pip install requests==2.10.0 - prevent some telegram api errors
import telepot
from datetime import datetime
from datetime import timedelta
import time
from web3 import Web3, HTTPProvider
from bs4 import BeautifulSoup
import mysql.connector

#set contract address
contractAddress="0x999dece6c9f47d0dabe96567d061944efc28e86d"
coinName="HVNN"
max_supply=400
token='' #HeavenTokenBot
channel="@heaventoken"

#config
ddex=0
forkdelta=0
usedb=1
uselink=0

def percentage(newval, oldval):
    diff=float(newval)-float(oldval)
    perc=round((diff*float(oldval)) / 100.0,2)
    if (perc<0):
        return str(perc)+"%"
    else:
        return "+"+str(perc)+"%"

#db_definition
mydb = mysql.connector.connect(
  host="localhost",
  user="",
  passwd="",
  database="bots"
)
# Only this particular cursor will buffer results
mycursor = mydb.cursor(buffered=True)

h1=timedelta(hours=1) #time interval for searching last coins
h24=timedelta(hours=24) #time interval for searching last coins


#insert here infura endpoint for the mainnet
web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/KEY"))
#get the bot
bot=telepot.Bot(token=token)


print ("Started")

#set some emoji
rocket=u'\U0001F680'
fire=u'\U0001F525' #burned
firecraker=u'\U0001F9E8'
chartUp=u'\U0001F4C8' #Dhigh
chartDown=u'\U0001F4C9' #Dlow
chartBar=u'\U0001F4CA' #Dvol
scream=u'\U0001F631' #remaining
bag=u'\U0001F4B0' #cap
diamond=u'\U0001F48E' #total
muscle=u'\U0001F4AA' #holders
explosion=u'\U0001F4A5' #last1h burn


print ("Load ABI")

#set standard ERC20 ABI
abi = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"type":"function"}]'
print ("Load contract address")

print ("Get Contract data")

#get total supply from contract
fuzec = web3.eth.contract(address=web3.toChecksumAddress(contractAddress),abi=abi)
ts = fuzec.functions.totalSupply().call()
ts_eth= web3.fromWei(ts, "ether")
burned=max_supply-ts_eth

td=diamond + " Total supply: "+str(max_supply)+ " " +coinName+"\n" +  fire + " Burned: " + str(round(burned,3)) + "  "+coinName+"\n" + scream + " Remaining: "+ str(round(ts_eth,3)) + "  "+coinName+"\n"


price=0
vol=0
low=0
high=0

price_usd=0
vol_usd=0
low_usd=0
high_usd=0

cap=0
cap_usd=0


if (ddex==1):
    # #Get DDEX data
    print ("Get DDEX data")
    r=requests.get("https://api.ddex.io/v3/markets/FUZE-WETH/ticker")
    json=r.json()["data"]["ticker"]

    # #parse data from response
    price=json["price"]
    vol=json["volume"]
    low=json["low"]
    high=json["high"]

    # #Get Coincalculator data
    print ("Get Coincalculator data")
    r=requests.get("https://www.coincalculators.io/api/price?ticker=eth")
    eth_usd=float(r.json()["averagePrice_USD"])

    price_usd=float(price)*eth_usd
    vol_usd=float(vol)*eth_usd
    low_usd=float(low)*eth_usd
    high_usd=float(high)*eth_usd

    cap=float(ts_eth)*float(price)
    cap_usd=cap*float(eth_usd)

if (usedb==1):
    #insert data into db
    sql="INSERT into " + coinName + " (supply,price,storage_datetime) VALUES(%s,%s,%s)"
    val = (ts_eth,price,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #print (sql)
    #print (val)
    #print (mycursor.execute(sql, val))
    mycursor.execute(sql, val)
    mydb.commit()

    #Get Holders from etherscan page
    print ('Get Holders from etherscan')
    req=requests.get("http://etherscan.io/token/"+contractAddress+"#balances")
    soup = BeautifulSoup(req.text, features="lxml")
    res=soup.find('div', {'id': 'ContentPlaceHolder1_tr_tokenHolders'}).find('div').find_all('div')[1].text
    holders=res[1:res.find(' addresses')]
    hmex= muscle + ' Holders: ' + holders
    hlist=' (Full list <a href="https://etherscan.io/token/'+contractAddress+'#balances">here</a>)\n\n'

    #get data from the db
    #get ann of last 1h from db
    sql = "SELECT price,supply FROM "+coinName+" WHERE storage_datetime>='"+str(datetime.now()-h1)+"' LIMIT 1"
    #print (mycursor.execute(sql))
    mycursor.execute(sql)
    data = mycursor.fetchall()[0]
    h1_price = data[0]
    h1_supply = data[1]

    #get ann of last 1h from db
    sql = "SELECT price,supply FROM "+coinName+" WHERE storage_datetime>='"+str(datetime.now()-h24)+"' LIMIT 24"
    #print (mycursor.execute(sql))
    mycursor.execute(sql)
    data = mycursor.fetchall()[0]
    h24_price = data[0]
    h24_supply = data[1]

if (uselink==1):
    #prepare links
    link='Trade '+ coinName +'  on <a href="https://ddex.io/trade/'+ coinName +'-WETH">ddex.io</a> and <a href="https://forkdelta.app/#!/trade/'+contractAddress+'-ETH">ForkDelta</a>!\n'

print ("Sending message")

h1_burned=float(h1_supply)-float(ts_eth)
#h1_priceVar=percentage(price, h1_price)

h24_burned=float(h24_supply)-float(ts_eth)
#h24_priceVar=percentage(price, h24_price)

burnMex_1h=explosion + " " + str(round(h1_burned,3)) + " " + coinName + " burned in last hour!!! " + explosion + "\n"
burnMex_24h=explosion + " " + str(round(h24_burned,3)) + " " + coinName + " burned in last day!!! " + explosion + "\n"

#prepare message
#lp=rocket + " Last Price " + price + " ETH  |  " + str(round(price_usd,3)) + " $ ( 1h: " + h1_priceVar + " - 24h: " + h24_priceVar + " )\n"
#pd1=chartDown + " Daily low: " + low + " ETH  |  " + str(round(low_usd,3)) + " $\n" + chartUp + " Daily high: " + high + " ETH  |  " + str(round(high_usd,3)) + " $\n"
#pd2=chartBar + " Daily volume: " + vol + " ETH  |  " + str(round(vol_usd,3)) + " $\n" +  bag + " Market Cap: " + str(round(cap,3)) + " ETH  |  " + str(round(cap_usd,3)) + " $\n\n"
mex= burnMex_1h + burnMex_24h + "\n" + td + hmex + hlist# + lp + pd1 + pd2 + link

#send message to telegram
bot.sendMessage(chat_id=channel, text=mex, parse_mode= 'HTML')

print ("Done")