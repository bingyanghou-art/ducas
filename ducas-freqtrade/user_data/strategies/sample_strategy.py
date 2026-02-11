from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class RsiVolumeStrategy(IStrategy):
    """
    A Freqtrade strategy based on RSI and volume conditions on 4h timeframe.
    - Entry: RSI(10) crosses above 30 and volume > 1.2 * mean of previous 10 volumes.
    - Stoploss: 1%
    - Trailing stoploss: Activates at 2% profit, with 0.5% trailing distance.
    No explicit exit signal; relies on stoploss and trailing.
    """

    INTERFACE_VERSION = 3

    # Strategy parameters
    timeframe = '4h'
    startup_candle_count: int = 10  # For RSI(10) and rolling(10)

    # Stoploss
    stoploss = -0.01  # 1%

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.005  # 0.5%
    trailing_stop_positive_offset = 0.02  # Activate at 2%
    trailing_only_offset_is_reached = True

    # Disable ROI and exit signals if not needed
    minimal_roi = {"0": 999}  # Effectively disable ROI exits
    use_exit_signal = False
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # RSI(10)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=10)

        # Mean volume of previous 10 candles (shifted to avoid lookahead bias)
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=10).mean().shift(1)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Entry conditions: RSI crosses above 30 and volume > 1.2 * previous mean volume
        dataframe.loc[
            (qtpylib.crossed_above(dataframe['rsi'], 30)) &
            (dataframe['volume'] > 1.2 * dataframe['volume_mean']),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # No explicit exit signal
        return dataframe