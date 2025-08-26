# Trade Bot

A simple Bitcoin trading strategy backtester and bot for fun and learning.  
The project demonstrates a MACD-based strategy and compares it against HODL.

## Files

- `backtester.ipynb` – Jupyter notebook for testing strategies.
- `bot.py` – Simple script for running the bot. This bot is designed to run 24/7 on a Raspberry Pi using a cronjob.

**Note:** The CSV with historical data for backtesting is available here: [Kaggle Dataset](https://www.kaggle.com/datasets/mouadjaouhari/bitcoin-hourly-ohclv-dataset?resource=download).


## About the Strategy

HODL naturally ends up being the most profitable approach, since Bitcoin’s value has grown exponentially over time.  
The trading strategy is **not** designed to outperform HODL in absolute returns. Its purpose is to **reduce risk**, limiting losses during market downturns while still capturing gains in uptrends.  
In other words, the strategy prioritizes smoother, less volatile growth rather than maximizing profit.

## License

`btc_hourly_ohclv.csv` is under the MIT License (see LICENSE file).  
Other code and files are free to use for learning and experimentation.
