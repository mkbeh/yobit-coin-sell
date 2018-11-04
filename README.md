### Description
Utility for yobit exchange which sell all coin amount by values from config file.

### Use:
* Start script once for create files: getme.cfg , nonce.cfg

###### getme.cfg contains 5 fields:
```angular2html
currency1:          # main currency which need to sell
currency2:btc       # currency for which we sell main currency
api_key:
secret_key:
lt:1            # minimal value. if currency1 amount > lt: script will sell main coins
```

* Set values into getme.cfg
* Run script again
* If you change your private keys - nullify your counter in nonce.cfg file.