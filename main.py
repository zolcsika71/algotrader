"""
algotrader
"""
import abc
import os
import warnings
from abc import ABC
import openai
import yfinance as yf
import pandas as pd
import json


class OpenAIAPI:
    """
    OpenAIAPI class to manage the OpenAI API key.
    """
    API_KEY_ENV_VAR = 'OPENAI_API_KEY'

    def __init__(self):
        self.load_api_key()

    def load_api_key(self):
        """
        Load the OpenAI API key from the environment variable.
        """
        api_key = os.getenv(self.API_KEY_ENV_VAR)
        assert api_key is not None, f"Missing {self.API_KEY_ENV_VAR} in environment variables"
        openai.api_key = api_key


class StockAPI(abc.ABC):
    """
    Abstract Base Class for all APIs
    """

    def __init__(self):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

    @abc.abstractmethod
    def fetch_and_format_stock_info(self, ticker_symbol: str):
        """
        Fetch and format stock information
        :param ticker_symbol:
        """
        print(f"Fetching and formatting stock information for {ticker_symbol}")

    @abc.abstractmethod
    def print_formatted_stock_actions(self, actions_df):
        """
        Print formatted stock actions
        :param actions_df:
        """
        pass


class BaseStockAPI(StockAPI, ABC):
    """
    BaseStockAPI class that implements common methods for YFActions and YFinanceAPI
    """

    def __init__(self):
        super().__init__()
        self.organized_actions = None
        self.current_ticker_symbol = None

    def print_formatted_stock_actions(self, actions_df):
        """
        Prints the stock actions once they've been formatted.
        """
        if self.current_ticker_symbol:
            print(f"Ticker: {self.current_ticker_symbol}")
        actions_df = actions_df[['type', 'date', 'value']]
        print(actions_df)

    def get_organized_stock_actions(self, ticker_symbol: str):
        """
        Organizes the stock actions based.
        """
        actions = ticker_symbol.actions
        if actions.empty:
            return None
        self.organized_actions = {}
        for index, row in actions.iterrows():
            for col_name in actions.columns:
                if action_value := row[col_name]:
                    self.organized_actions.setdefault(col_name, []).append({'date': index.strftime('%Y-%m-%d'), 'value': action_value})
        return self.organized_actions or None

    def create_stock_records_df(self, actions_df):
        """
        Creates a DataFrame to hold all the stock records.
        """
        for action_type, records in self.organized_actions.items():
            temp_df = pd.DataFrame(records)
            temp_df['type'] = action_type
            actions_df = pd.concat([actions_df, temp_df], ignore_index=True)
        return actions_df


class YFActions(BaseStockAPI):
    """
    YFActions class to fetch and format stock Dividends and Stock Splits from yfinance.
    """

    def __init__(self):
        super().__init__()
        self.ignore_warnings()

    @staticmethod
    def ignore_warnings():
        """
        Method to ignore any warnings that might occur while fetching the stock data.
        """
        warnings.filterwarnings("ignore", category=FutureWarning)

    def fetch_and_format_stock_info(self, ticker_symbol: str):
        print(f"Ticker: {ticker_symbol}")
        ticker = yf.Ticker(ticker_symbol)
        self.handle_stock_actions(ticker, ticker_symbol)

    def handle_stock_actions(self, ticker, ticker_symbol):
        """
        Handles the stock actions for the provided ticker.
        :param ticker:
        :param ticker_symbol:
        """
        if self.get_organized_stock_actions(ticker):
            actions_df = self.create_stock_records_df(pd.DataFrame())
            if not actions_df.empty:
                self.print_formatted_stock_actions(actions_df)
        else:
            print(f"No actions found for ticker {ticker_symbol}.")


class YFinanceAPI(BaseStockAPI):
    def __init__(self, ticker: str = None):
        super().__init__()
        self.ticker_symbol = ticker
        self.yf_actions = YFActions()

    def fetch_and_format_stock_info(self, ticker_symbol: str):
        """
        Fetch and format stock information using YFActions.
        """
        print(f"Fetching and formatting stock information for {ticker_symbol}")
        self.yf_actions.fetch_and_format_stock_info(ticker_symbol)

    def run(self):
        """
        Run the YFinanceAPI to fetch and format stock information.
        """
        self.fetch_and_format_stock_info(self.ticker_symbol)


class PortfolioManager:
    """
    PortfolioManager class to manage a portfolio of stocks.
    """

    def __init__(self, portfolio_file, stock_api):
        """
        Initialize the PortfolioManager with a portfolio file and a stock API object.
        :param portfolio_file: Path to the portfolio JSON file.
        :param stock_api: An instance of a StockAPI subclass to fetch stock information.
        """
        self.portfolio_file = portfolio_file
        self.stock_api = stock_api

    def load_portfolio(self):
        """
        Loads the portfolio from a JSON file (portfolio.json)
        :return:
        """
        try:
            with open(self.portfolio_file) as file:
                portfolio = json.load(file)
            print(f"Portfolio loaded from {self.portfolio_file}")
        except FileNotFoundError:
            print(f"Couldn't load the portfolio. No such file: {self.portfolio_file}")
            portfolio = None
        return portfolio

    def check_portfolio(self):
        """
        Checks the portfolio and prints the stock actions
        for each stock in the portfolio using the provided stock API instance
        """
        portfolio = self.load_portfolio()

        for stock in portfolio:
            self.stock_api.fetch_and_format_stock_info(stock['ticker'])


def main():
    """
    Main function to show the use of PortfolioManager.
    """
    openai_api = OpenAIAPI()
    stock_api = YFinanceAPI()
    portfolio_manager = PortfolioManager('portfolio.json', stock_api)
    portfolio_manager.check_portfolio()


if __name__ == '__main__':
    main()
