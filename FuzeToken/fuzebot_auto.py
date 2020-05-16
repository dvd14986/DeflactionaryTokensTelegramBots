#fuzebot V1.4 - released 01 feb 2020
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
import urllib.request

hdr = {
    'User-Agent': 'Mozilla/5.0',
    'Accept-Language': 'en-US,en;q=0.8'
    }

channel="@FUZE_Token"
backup_channel="" #bot test channel

#set contract address
contractAddress="0x187d1018e8ef879be4194d6ed7590987463ead85"
coinName="FUZE"
max_supply=1000
token='' #FuzeReportBot


#config
ddex=1
forkdelta=1
usedb=1
uselink=1

def percentage(newval, oldval):
    old=float(oldval)
    new=float(newval)
    perc=round(((new-old)/old)*100.0,2)
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

h1=timedelta(hours=1,minutes=10) #time interval for searching last coins
h24=timedelta(hours=24,minutes=10) #time interval for searching last coins


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
    #print ("Get DDEX data")
    #r=requests.get("https://api.ddex.io/v3/markets/FUZE-WETH/ticker")
    #json=r.json()["data"]["ticker"]

    #get Mercatox data
    print ("Get Mercatox data")
    r=requests.get("https://mercatox.com/api/public/v1/ticker")
    json_btc=r.json()["FUZE_BTC"]
    json_eth=r.json()["FUZE_ETH"]
    # #parse data from response
    price_btc=json_btc["last_price"]
    vol_btc=json_btc["quote_volume"]
    low_btc=json_btc["low24hr"]
    high_btc=json_btc["high24hr"]
    h24change_btc=float(json_btc["percentChange"])

    price_eth=json_eth["last_price"]
    vol_eth=json_eth["quote_volume"]
    low_eth=json_eth["low24hr"]
    high_eth=json_eth["high24hr"]
    h24change_eth=float(json_eth["percentChange"])

    # #Get Coincalculator data
    print ("Get Coincalculator data")
    r=requests.get("https://www.coincalculators.io/api/price?ticker=eth")
    eth_usd=float(r.json()["averagePrice_USD"])

    r=requests.get("https://www.coincalculators.io/api/price?ticker=btc")
    btc_usd=float(r.json()["averagePrice_USD"])

    price_usd_btc=float(price_btc)*btc_usd
    vol_usd_btc=float(vol_btc)*btc_usd
    low_usd_btc=float(low_btc)*btc_usd
    high_usd_btc=float(high_btc)*btc_usd

    price_usd_eth=float(price_eth)*eth_usd
    vol_usd_eth=float(vol_eth)*eth_usd
    low_usd_eth=float(low_eth)*eth_usd
    high_usd_eth=float(high_eth)*eth_usd

    cap_btc=float(ts_eth)*float(price_btc)
    cap_eth=float(ts_eth)*float(price_eth)

    cap_usd_btc=cap_btc*float(btc_usd)
    cap_usd_eth=cap_eth*float(eth_usd)
    cap_usd_avg=(cap_usd_btc+cap_usd_eth)/2

if (usedb==1):
    print ("Write data in db")
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
    attempt=0
    hmex=muscle
    #hlist=' (Full Holders list <a href="https://etherscan.io/token/'+contractAddress+'#balances">here</a>)\n\n'
    while attempt<3:
        try:
            print ("Attempt " + str(attempt) + "...")
            #req=requests.get("http://etherscan.io/token/"+contractAddress+"#balances", timeout=10)
            req = urllib.request.Request("http://etherscan.io/token/"+contractAddress+"#balances",headers=hdr)
            with urllib.request.urlopen(req) as f:
                txt=(f.read().decode('utf-8'))
            soup = BeautifulSoup(txt, features="lxml")
            res=soup.find('div', {'id': 'ContentPlaceHolder1_tr_tokenHolders'}).find('div').find_all('div')[1].text
            holders=res[1:res.find(' addresses')]
            hmex= muscle + ' Holders: ' + holders
            break
        except:
            print("Attempt " + str(attempt) + " failed.")
            attempt+=1

    #get data from the db
    #get ann of last 1h from db
    #print ("Get 1h data from db")
    #sql = "SELECT price,supply FROM "+coinName+" WHERE storage_datetime>='"+str(datetime.now()-h1)+"' LIMIT 1"
    #print (mycursor.execute(sql))
    #mycursor.execute(sql)
    #data = mycursor.fetchall()[0]
    #h1_price = data[0]
    #h1_supply = data[1]

    #get ann of last 1h from db
    print ("Get 4h data from db")
    sql = "SELECT price,supply FROM "+coinName+" WHERE storage_datetime>='"+str(datetime.now()-h24)+"' LIMIT 24"
    #print (mycursor.execute(sql))
    mycursor.execute(sql)
    data = mycursor.fetchall()[0]
    h24_price = data[0]
    h24_supply = data[1]

if (uselink==1):
    #prepare links
    link0="We're on MERCATOX! Trade " + coinName + " in pair with <a href='https://mercatox.com/exchange/"+ coinName +"/ETH'>ETH</a> or <a href='https://mercatox.com/exchange/"+ coinName +"/BTC'>BTC</a>!\n\n"
    link='Trade '+ coinName +' also on <a href="https://ddex.io/trade/'+ coinName +'-WETH">ddex.io</a> and <a href="https://forkdelta.app/#!/trade/'+contractAddress+'-ETH">ForkDelta</a>!\n'

print ("Sending message")

#h1_burned=float(h1_supply)-float(ts_eth)
#h1_priceVar=percentage(price, h1_price)

h24_burned=float(h24_supply)-float(ts_eth)
#h24_priceVar=percentage(price, h24_price)

#burnMex_1h=explosion + " " + str(round(h1_burned,3)) + " " + coinName + " burned in last hour!!! " + explosion + "\n"
burnMex_24h=explosion + " " + str(round(h24_burned,3)) + " " + coinName + " burned in last day!!! " + explosion + "\n"

#prepare message
lp_btc=rocket + " Last Price " + price_btc + " BTC  |  " + str(round(price_usd_btc,3)) + " $ ( 24h: " + str(round(h24change_btc,3)) + "% )\n"
pd1_btc=chartDown + " Daily low: " + low_btc + " BTC  |  " + str(round(low_usd_btc,3)) + " $\n" + chartUp + " Daily high: " + high_btc + " BTC  |  " + str(round(high_usd_btc,3)) + " $\n"
pd2_btc=chartBar + " Daily volume: " + vol_btc + " BTC  |  " + str(round(vol_usd_btc,3)) + " $\n"

lp_eth=rocket + " Last Price " + price_eth + " ETH  |  " + str(round(price_usd_eth,3)) + " $ ( 24h: " + str(round(h24change_eth,3)) + "% )\n"
pd1_eth=chartDown + " Daily low: " + low_eth + " ETH  |  " + str(round(low_usd_eth,3)) + " $\n" + chartUp + " Daily high: " + high_eth + " ETH  |  " + str(round(high_usd_eth,3)) + " $\n"
pd2_eth=chartBar + " Daily volume: " + vol_eth + " ETH  |  " + str(round(vol_usd_eth,3)) + " $\n"
#mex= burnMex_1h + burnMex_24h + "\n" + td + hmex + hlist + lp + pd1 + pd2 + link
mkcap=bag + " Market Cap: " + str(round(cap_btc,3)) + " BTC  |  " +str(round(cap_eth,3)) + " ETH  |  " + str(round(cap_usd_avg,3)) + " $\n\n"
mex=burnMex_24h + "\n" + td + hmex + "\n\nBTC MARKET\n" + lp_btc + pd1_btc + pd2_btc + "\nETH MARKET\n" + lp_eth + pd1_eth + pd2_eth + "\n" + mkcap #+ link0 + link hlist

#send message to telegram
bot.sendMessage(chat_id=channel, text=mex, parse_mode= 'HTML')
bot.sendMessage(chat_id=backup_channel, text=mex, parse_mode= 'HTML')

print ("Done")
