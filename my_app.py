# Import Library
from re import I
import streamlit as st
import requests as rq
import pandas as pd
import altair as alt

# configuration theme
st.set_page_config(layout="wide")
st.header('Traderjoe Fees Calculator')

# initiate global variables
data_pools = []
select_pools = {}
liquidity = {
    "date" : [],
    "liquidity": []
}
volumes={
    "date" : [],
    "volumes": []
}
result = False

# get initial data pools
with st.spinner('Wait for it...'):
    r = rq.get('https://api.covalenthq.com/v1/43114/xy=k/traderjoe/pools/?quote-currency=USD&format=JSON&&page-size=99999&key={}'.format(st.secrets.api_key))
    data_items = r.json()["data"]["items"]
    token0 = ''
    token1 = ''
    for i in data_items :

        # Get Pools Name if null then use contract address
        if i["token_0"]["contract_ticker_symbol"] is not None and i["token_0"]["contract_ticker_symbol"] != '' :
            token0 = i["token_0"]["contract_ticker_symbol"]
        else :
            token0 = i["token_0"]["contract_address"]

        if i["token_1"]["contract_ticker_symbol"] is not None and i["token_1"]["contract_ticker_symbol"] != '' :
            token1 = i["token_1"]["contract_ticker_symbol"]
        else :
            token1 = i["token_1"]["contract_address"]

        # basically remove pools with contract decimals 0 because it will break the values
        if i["token_0"]["contract_decimals"] != 0 and i["token_1"]["contract_decimals"] != 0 :
            data_pools.append("{} - {}".format(token0, token1))
            select_pools["{} - {}".format(token0, token1)] = i['exchange']

# form calculation
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
        result = False
        r = rq.get('https://api.covalenthq.com/v1/43114/xy=k/traderjoe/pools/address/{}/?quote-currency=USD&format=JSON&key={}'.format(select_pools[option], st.secrets.api_key))
        data_address = r.json()
        estimated_fee = (number / data_address["data"]["items"][0]["total_liquidity_quote"])*data_address["data"]["items"][0]["fee_24h_quote"]
        metric1, metric2, metric3, metric4 = st.columns(4)
        with metric1:
            st.metric(label="Estimated Daily Fee", value="$ {:,.2f}".format(estimated_fee))
        with metric2:
            st.metric(label="Estimated Weekly Fee", value="$ {:,.2f}".format(estimated_fee*7))
        with metric3:
            st.metric(label="Estimated Monthly Fee", value="$ {:,.2f}".format(estimated_fee*30))
        with metric4:
            st.metric(label="Estimated Yearly Fee", value="$ {:,.2f}".format(estimated_fee*365))
        # Get Data Liquidity 7D
        for i in data_address["data"]["items"][0]["liquidity_timeseries_7d"] :
            liquidity["date"].append(i["dt"])
            liquidity["liquidity"].append(i["liquidity_quote"])
        # Get Data Volumes 7D
        for i in data_address["data"]["items"][0]["volume_timeseries_7d"] :
            volumes["date"].append(i["dt"])
            volumes["volumes"].append(i["volume_quote"])
        result = True

if result : 
    with st.expander("See Details {} Pools".format(option)):
        metric1, metric2, metric3, metric4 = st.columns(4)
        with metric1:
            st.metric(label="Totao Liquidity", value="$ {:,.2f}".format(data_address["data"]["items"][0]["total_liquidity_quote"]), delta="{:,.2f}".format(data_address["data"]["items"][0]["total_liquidity_quote"] - liquidity["liquidity"][len(liquidity["liquidity"])-2]))
        with metric2:
            st.metric(label="Daily Volumes", value="$ {:,.2f}".format(data_address["data"]["items"][0]["volume_24h_quote"]), delta="{:,.2f}".format(data_address["data"]["items"][0]["volume_24h_quote"] - volumes["volumes"][len(volumes["volumes"])-2]))
        with metric3:
            st.metric(label="APY", value="{:,.2f} %".format(data_address["data"]["items"][0]["annualized_fee"]*100))
        with metric4:
            st.metric(label="Daily Swaps", value="{:,.0f}".format(data_address["data"]["items"][0]["swap_count_24h"]))
        chart1, chart2 = st.columns(2)
        with chart1 :
            st.subheader('Daily Liquidity')
            df = pd.DataFrame(liquidity, columns=["date", "liquidity"])
            c = alt.Chart(df).mark_area(
                line={'color':'darkgreen'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='white', offset=0),
                        alt.GradientStop(color='darkgreen', offset=1)],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0
                )
            ).encode(
                alt.X('date:T'),
                alt.Y('liquidity:Q')
            )

            st.altair_chart(c, use_container_width=True)
        with chart2 :
            st.subheader('Daily Volumes')
            df = pd.DataFrame(volumes, columns=["date", "volumes"])
            c = alt.Chart(df).mark_area(
                line={'color':'darkgreen'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='white', offset=0),
                        alt.GradientStop(color='darkgreen', offset=1)],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0
                )
            ).encode(
                alt.X('date:T'),
                alt.Y('volumes:Q')
            )

            st.altair_chart(c, use_container_width=True)