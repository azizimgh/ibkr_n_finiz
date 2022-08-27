

# Genaral setting:
forced_run = True # Run the code without taking into consideration timz . Use it for testing
budget_pertrade = 1000 # dollars
start_hour= 9
start_min = 30



##### Finiz website:
url_1 = 'https://finviz.com/screener.ashx?v=320&s=n_majornews'
url_2 = 'https://finviz.com/screener.ashx?v=320&s=n_majornews&r=11'

urls = [url_1,url_2]


#### Data archiving

scrpaed_data = "data/scraped"
traded_data = "data/traded"
log_data = "logs"


#### Trader work station settings

tws_port = 7497
account_type = 'test'
allow_delayed_data = True


#### Strategy 1
use_strategy_1 =  True
strat1_minutes_to_consider = 5 # First minutes
strat1_decrease = -2 #%


#### Strategy 2
use_strategy_2 =  True
strat2_minutes_to_consider = 5 # First minutes
strat2_earnins = ["today_before", "yesterday_after"]
strat2_decrease = -2 #%


#### Strategy 3
use_strategy_3 =  True
strat3_minutes_to_consider = 5 # First minutes
return_open_low = 20 #The return between the open price and the low of the past two trading days 
strat3_decrease = -2 #%


### Trading check
ipo_check= 30 # number of days 