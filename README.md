# DeflactionaryTokensTelegramBots
A collection of some deflactionary tokens alert telegram bots, built from scratch with the same structure and customized on token's devs requests.

Bots gets data directly from Ethereum blockchian and from different market or data services if available.
Mysql db is used to store data for each execution to provide stats of burned coin, price variation and so on.

In the early stages price variation must be calc using db data because no api is available.

When token will list in a better exchange, like Mercatox, some price variation data starts to be available and could be gets using Mercatox api or other provider like coincalculators.io. Check Fuzebot that is the most update version of the bot.

Scripts take number of token holder directly from etherscan token's page. After Etherscan move behind cluodflare protection, differet type of requests must be using to get that data. Check Fuzebot.


## Installation
Create a mysql db called bots and create table you need into that DB. Can use located sql script in each folder to create a table.

*pip install requests*

In some systems last update of requests library could cause problem with web3. To solve the issue use version 2.10.0 of requests
*pip install requests==2.10.0*

*pip install web3*

*pip install mysql.connector*

*pip intall bs4*

*pip install telepot*

## Telegram Configuration
Talk with @BotFather to create new bot and get bot token.

Check this to know how to get the channel id. https://stackoverflow.com/questions/33858927/how-to-obtain-the-chat-id-of-a-private-telegram-channel

For public channel, use @usinfobot to get the id or use group/channel username. 

## Usage
Simply execute script from python3 when you need. You can add in cron or windows scheduler to run when you need.