import yfinance as yf
import pandas as pd
import json
import openai
import os

def token():
    key = 'OPENAI_API_KEY'
    value = os.getenv(key)
    openai.api_key = value

def print_hi(name):
    """
    This is a sample function to print a message
    :param name:
    """
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
