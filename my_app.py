from re import I
import streamlit as st
import requests as rq
import time

# configuration theme
st.set_page_config(layout="wide")
st.header('Traderjoe Fees Calculator')

# initiate global variables
data_pools = []
select_pools = {}

# form calculation
with st.spinner('Wait for it...'):
    r = rq.get('https://api.covalenthq.com/v1/43114/xy=k/traderjoe/pools/?quote-currency=USD&format=JSON&&page-size=99999&key=ckey_4e7ba38c8e50410a92ed0989d8f')
    data_items = r.json()["data"]["items"]
    token0 = ''
    token1 = ''
    for i in data_items :
        if i["token_0"]["contract_ticker_symbol"] is not None and i["token_0"]["contract_ticker_symbol"] != '' :
            token0 = i["token_0"]["contract_ticker_symbol"]
        else :
            token0 = i["token_0"]["contract_address"]

        if i["token_1"]["contract_ticker_symbol"] is not None and i["token_1"]["contract_ticker_symbol"] != '' :
            token1 = i["token_1"]["contract_ticker_symbol"]
        else :
            token1 = i["token_1"]["contract_address"]
        if i["token_0"]["contract_decimals"] != 0 and i["token_1"]["contract_decimals"] != 0 :
            data_pools.append("{} - {}".format(token0, token1))
            select_pools["{} - {}".format(token0, token1)] = i['exchange']

with st.form("my_form"):
    col1, col2 = st.columns(2)
    with col1:
        number = st.number_input('Amount investment in $USD')

    with col2:
        option = st.selectbox(
        'Select The Pools',
        data_pools)
    submitted = st.form_submit_button("Submit")
    if submitted:
        r = rq.get('https://api.covalenthq.com/v1/43114/xy=k/traderjoe/pools/address/{}/?quote-currency=USD&format=JSON&key=ckey_4e7ba38c8e50410a92ed0989d8f'.format(select_pools[option]))
        data_address = r.json()
        st.write(data_address)
