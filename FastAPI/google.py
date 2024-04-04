from googlesearch import search
import re

results = search("大新 stock symbol", advanced=True, num_results=1)
title = next(results).title

# Define a pattern to match the stock and symbol
pattern = r"(.+)\((.+)\)"

# Use the search() method to find the first match and extract the stock and symbol
match = re.search(pattern, title)
stock, symbol = match.groups()

print(f"Stock: {stock}")
print(f"Symbol: {symbol}")
