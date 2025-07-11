import backtrader as bt
import pandas as pd

class ZoneRecoveryEA(bt.Strategy):
    params = (
        ('start_lot', 0.1),
        ('recovery_distance', 8),
        ('take_profit', 15),
        ('stop_loss', 30),
        ('initial_direction', 'long')
    )
    
    def __init__(self):
        self.last_entry_price = None
        self.recovery_level = 0
        self.lot_size = self.p.start_lot
        
    def next(self):
        if self.last_entry_price is None:
            self.open_initial_position()
            return
            
        distance = abs(self.data.close[0] - self.last_entry_price) * 10000
        if distance >= self.p.recovery_distance:
            self.open_recovery_position()
    
    def open_initial_position(self):
        self.last_entry_price = self.data.close[0]
        if self.p.initial_direction == 'long':
            self.buy(size=self.lot_size)
        else:
            self.sell(size=self.lot_size)
    
    def open_recovery_position(self):
        self.lot_size *= 2
        self.recovery_level += 1
        self.last_entry_price = self.data.close[0]
        
        if self.recovery_level % 2 == 1:
            if self.p.initial_direction == 'long':
                self.sell(size=self.lot_size)
            else:
                self.buy(size=self.lot_size)
        else:
            if self.p.initial_direction == 'long':
                self.buy(size=self.lot_size)
            else:
                self.sell(size=self.lot_size)

# Backtestni boshlash
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    
    # Ma'lumotlarni yuklash
    data = bt.feeds.GenericCSVData(
        dataname='data/DAT_MT_EURUSD_M1_202506.csv',
        dtformat=('%Y-%m-%d %H:%M:%S'),
        datetime=0, open=1, high=2, low=3, close=4, volume=5,
        timeframe=bt.TimeFrame.Minutes
    )
    cerebro.adddata(data)
    
    # Strategiyani qo'shish
    cerebro.addstrategy(ZoneRecoveryEA)
    
    # Backtest parametrlari
    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.0005)
    
    print('Boshlang\'ich balans: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Yakuniy balans: %.2f' % cerebro.broker.getvalue())
    
    # Natijalarni chizish
    cerebro.plot(style='candlestick')
