import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tushare as ts

# 设置 Tushare Token
ts.set_token('eff296515729fa175fc421d8eebcc1d2e9b68a6dd17d9953cb7df34f')
pro = ts.pro_api()

# 添加 easy_test 的路径（如使用）
sys.path.append(r"D:\实习\bridge_test_template")
from easy_test.backtest import BacktestEngine


# === 获取期货日线数据 ===
def get_futures_data(ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = pro.fut_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    if df.empty:
        raise ValueError(f"未找到合约 {ts_code} 的数据")
    df = df[['trade_date', 'close']]
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df.set_index('trade_date', inplace=True)
    df.sort_index(inplace=True)
    return df


# === 双均线策略 ===
class DoubleMAStrategy:
    def __init__(self, fast=5, slow=10):
        self.fast = fast
        self.slow = slow

    def handle_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df['MA_fast'] = df['close'].rolling(self.fast).mean()
        df['MA_slow'] = df['close'].rolling(self.slow).mean()
        df['signal'] = 0
        df.loc[(df['MA_fast'] > df['MA_slow']) & (df['MA_fast'].shift(1) <= df['MA_slow'].shift(1)), 'signal'] = 1
        df.loc[(df['MA_fast'] < df['MA_slow']) & (df['MA_fast'].shift(1) >= df['MA_slow'].shift(1)), 'signal'] = -1
        return df


# === BARSLAST 实现 ===
def BARSLAST(condition: pd.Series) -> pd.Series:
    barslast = []
    last_index = -1
    for i, cond in enumerate(condition):
        if cond:
            last_index = i
            barslast.append(0)
        elif last_index == -1:
            barslast.append(np.nan)
        else:
            barslast.append(i - last_index)
    return pd.Series(barslast, index=condition.index)


# === 主函数 ===
if __name__ == '__main__':
    ts_code = 'CU9999.SHF'
    start_date = '20220101'
    end_date = '20221231'

    try:
        df = get_futures_data(ts_code, start_date, end_date)
    except ValueError as e:
        print(e)
        exit()

    # 应用策略
    strategy = DoubleMAStrategy(fast=5, slow=10)
    df = strategy.handle_data(df)

    # 示例：BARSLAST
    print("BARSLAST 示例（close == 4300）:")
    print(BARSLAST(df['close'] == 4300).tail())

    # 回测与绘图
    engine = BacktestEngine()
    result = engine.run_backtest(df, signal_column='signal')
    engine.plot_result(result)
