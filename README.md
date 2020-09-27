


### proj: translate X currency to selected currency types,
# for example: USD to:
    # 1. UK sterling
    # 2. Euro
    # 3. NIS


1. get updated exchange rates
    # bank of israel API: 
        #https://www.boi.org.il/he/Markets/Pages/explainxml.aspx
    3 !async! requests - 
        https://www.boi.org.il/currency.xml?curr=01
        https://www.boi.org.il/currency.xml?curr=02
        https://www.boi.org.il/currency.xml?curr=27
2. ask user for input -> num
3. ask user for currency types
4. show results 

