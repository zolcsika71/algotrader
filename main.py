"""
algotrader
"""
import abc
import os
import warnings
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


class YFinanceAPI(StockAPI):
    def __init__(self):
        super().__init__()
        self.organized_actions = None
        self.ignore_warnings()
        self.current_ticker_symbol = None  # Add an instance variable for the ticker symbol

    @staticmethod
    def ignore_warnings():
        """
        Ignore warnings from libraries
        """
        warnings.filterwarnings("ignore", category=FutureWarning)

    def print_formatted_stock_actions(self, actions_df):
        """
        Print formatted stock actions
        :param actions_df:
        """
        if self.current_ticker_symbol:  # Check if the ticker symbol is set
            print(f"Ticker: {self.current_ticker_symbol}")
        actions_df = actions_df[['type', 'date', 'value']]
        print(actions_df)

    @staticmethod
    def init_and_add_stock_records(organized_actions, actions_df):
        """
        Initialize and add stock records
        :param organized_actions:
        :param actions_df:
        :return:
        """
        for action_type, records in organized_actions.items():
            temp_df = pd.DataFrame(records)
            temp_df['type'] = action_type
            actions_df = pd.concat([actions_df, temp_df], ignore_index=True)
        return actions_df

    def get_organized_stock_actions(self, ticker_symbol: str):
        """
        Get organised stock actions
        :param ticker_symbol:
        :return:
        """
        actions = ticker_symbol.actions
        if actions.empty:
            return None
        self.organized_actions = {}  # Use self to make it an instance variable
        for index, row in actions.iterrows():
            for col_name in actions.columns:
                if action_value := row[col_name]:
                    self.organized_actions.setdefault(col_name, []).append({'date': index.strftime('%Y-%m-%d'), 'value': action_value})
        return self.organized_actions or None

    def fetch_and_format_stock_info(self, ticker_symbol):
        print(f"Ticker: {ticker_symbol}")  # print ticker name here
        ticker = yf.Ticker(ticker_symbol)
        self.handle_stock_actions(ticker, ticker_symbol)

    def handle_stock_actions(self, ticker, ticker_symbol):
        """
        Handle stock actions
        :param ticker:
        :param ticker_symbol
        """
        if self.get_organized_stock_actions(ticker):
            actions_df = self.create_stock_records_df(pd.DataFrame())
            if not actions_df.empty:
                self.print_formatted_stock_actions(actions_df)
        else:
            print(f"No actions found for ticker {ticker_symbol}.")

    def create_stock_records_df(self, actions_df):
        """
        Create stock records dataframe
        :param actions_df:
        :return:
        """
        for action_type, records in self.organized_actions.items():
            temp_df = pd.DataFrame(records)
            temp_df['type'] = action_type
            actions_df = pd.concat([actions_df, temp_df], ignore_index=True)
        return actions_df


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
        Load the portfolio from the portfolio file.
        :return:
        """
        try:
            with open(self.portfolio_file) as f:
                return json.load(f)
        except FileNotFoundError:
            print("portfolio.json file not found.")
            return []

    def check_portfolio(self):
        """
        Check the portfolio and print the stock actions.
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
