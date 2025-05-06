
import sys
import os
import pandas as pd
import numpy as np

# 添加 easy_test 的上层路径
sys.path.append(r"D:\实习\bridge_test_template")

from easy_test.backtest import BacktestEngine

class DoubleMAStrategy:
    def __init__(self, fast=5, slow=10):
        self.fast = fast
        self.slow = slow

    def handle_data(self, df: pd.DataFrame):
        df['MA_fast'] = df['close'].rolling(self.fast).mean()
        df['MA_slow'] = df['close'].rolling(self.slow).mean()
        df['signal'] = 0

        # 生成交易信号：金叉做多，死叉平仓
        df.loc[(df['MA_fast'] > df['MA_slow']) & (df['MA_fast'].shift(1) <= df['MA_slow'].shift(1)), 'signal'] = 1
        df.loc[(df['MA_fast'] < df['MA_slow']) & (df['MA_fast'].shift(1) >= df['MA_slow'].shift(1)), 'signal'] = -1

        return df

def BARSLAST(condition: pd.Series) -> pd.Series:
    """
    返回上一次满足条件的位置距离当前的周期数。若未曾满足过，则返回 NaN。
    """
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

if __name__ == '__main__':
    # 加载数据：可替换为任意支持的国内期货品种
    engine = BacktestEngine()
    df = engine.load_data_from_csv("D:/实习/example_futures_data.csv")


    # 应用策略
    strategy = DoubleMAStrategy()
    df = strategy.handle_data(df)

    # 示例：使用BARSLAST函数
    example = BARSLAST(df['close'] == 3500)
    print("BARSLAST示例结果：")
    print(example.tail())

    # 回测
    result = engine.run_backtest(df, signal_column='signal')
    engine.plot_result(result)
