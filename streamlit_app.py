import streamlit as st
import backtrader as bt
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

# Define the trading strategy
class SmaCross(bt.Strategy):
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30   # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy()  # enter long

        elif self.crossover < 0:  # in the market & cross to the downside
            self.close()  # close long position

# Function to run backtest and return cerebro
def run_backtest(data):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross)
    feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(feed)
    cerebro.broker.setcash(10000)
    cerebro.addsizer(bt.sizers.AllInSizer, percents=95)  # Use 95% of the portfolio for each trade
    cerebro.run()
    return cerebro

# Initialize session state for running status
if 'running' not in st.session_state:
    st.session_state.running = False

# Streamlit app layout
st.title('Cryptocurrency Trading Bot Simulation')

# container for user input
st.header('User Input Parameters')
selected_crypto = st.selectbox('Select cryptocurrency', ('BTC-USD', 'ETH-USD', 'LTC-USD'))
start_date = st.date_input('Start date', datetime(2020, 1, 1))
end_date = st.date_input('End date', datetime(2021, 1, 1))

# Function to handle start button
def start_bot():
    st.session_state.running = True

# Function to handle stop button
def stop_bot():
    st.session_state.running = False

# Buttons to start/stop the bot
st.button('Start Bot', on_click=start_bot)
st.button('Stop Bot', on_click=stop_bot)

# Display bot status
if st.session_state.running:
    st.success('Bot is running!')
    # Fetch historical data from yfinance
    data = yf.download(selected_crypto, start=start_date, end=end_date)
    
    # Check if data was successfully fetched
    if not data.empty:
        # Run backtest
        cerebro = run_backtest(data)

        # Show results
        st.header('Simulation Results')
        st.write(f'Final Portfolio Value: ${cerebro.broker.getvalue():,.2f}')
        
        # Plot the results manually using matplotlib
        fig, ax = plt.subplots()
        for data in cerebro.datas:
            ax.plot(data.datetime.array, data.close.array, label='Close')
            ax.legend()
        
        # Show the plot
        st.pyplot(fig)
else:
    st.error('Bot is stopped!')
