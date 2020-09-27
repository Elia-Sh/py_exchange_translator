


## Instructions
```
1. git clone; 
2. cd into the cloned repository
3. python3 -m venv
4. source venv/bin/activate
5. pip install -r requirements.txt
```


### Usage as web service -
1. Start flask app by:  
`python flask_app.py`

2. Query the server -  
`http://127.0.0.1:5000/?amount=20&currency=USD`  
or get the exchange rate to NIS with no arguments -  
`http://127.0.0.1:5000/`


### command line usage:
    python exchange_translator.py 20 USD

