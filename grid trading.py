class Strategy(StrategyBase):
    def __init__(self):
        # strategy attributes
        self.period = 60*60
        self.subscribed_books = {
            'FTX': {
                'pairs': ['BTC-USD'],
            },
        }
        self.options = {}

        # define your attributes here
        self.upper = 54000
        self.lower = 40000
        self.average = 47800
        self.fee = 0.07
        self.number = 60
        self.amount = 1.5
        self.total_trade = 0
        self.total_transaction = 0

        self.buy_line = [ int((self.average - self.lower ) / ( self.number/2) * i )+ int(self.lower)\
                             for i in range(int(self.number/2)) ]
        self.sell_line = [ int((self.upper - self.average ) / ( self.number/2) * i )+ int(self.average)\
                             for i in range(int(self.number/2)) ]
        self.last_line = 0
        pass

    def on_order_state_change(self,  order):
        pass

    def trade(self, candles):
        exchange, pair, base, quote = CA.get_exchange_pair()
        # Log(str(self.sell_line.reverse()))

        target_currency_amount = self['assets'][exchange][quote]
        close_price = candles[exchange][pair][0]['close']

        singal = 0 #  1 for buy, -1 for sell
        cur_line = 0
        if close_price > self.average:
            for  line in self.sell_line:
                idx = self.sell_line.index(line)
                if(close_price < line):
                    cur_line = self.sell_line[idx-1]
                    break
        else:
            for line in self.buy_line:
                idx = self.buy_line.index(line)
                if(close_price > line):
                    cur_line = self.buy_line[idx-1]
                    break
        if self.last_line != cur_line:
            if close_price > self.average:
                signal = -1
            else:
                signal = 1
            self.last_line = cur_line
        else:
            signal = 0
        # Log(str(close_price) + "  " + str(cur_line) + "  " + str(signal))
        self.total_trade +=1
        if self.total_trade > 310 and signal == 1: # 最後一天不買
            signal = 0

        if signal == 1:
                CA.log('Buy ' + base)
                self.last_type = 'buy'
                CA.buy(exchange, pair, self.amount, CA.OrderType.MARKET)
                self.total_transaction += 1
        # place sell order
        elif signal == -1:
            CA.log('Sell ' + base)
            self.last_type = 'sell'
            CA.sell(exchange, pair, self.amount * (1- self.fee/100), CA.OrderType.MARKET)
            self.total_transaction += 1
        
        # prevent no transaction for 4 days long
        if self.total_trade > 100 and self.total_transaction == 0:
            diff = close_price - self.average
            self.average = close_price
            self.upper += diff
            self.lower += diff
            self.buy_line = [ int((self.average - self.lower ) / ( self.number/2) * i )+ int(self.lower)\
                            for i in range(int(self.number/2)) ]
            self.sell_line = [ int((self.upper - self.average ) / ( self.number/2) * i )+ int(self.average)\
                            for i in range(int(self.number/2)) ]
            self.amount = (self['assets'][exchange][quote] / close_price ) * 0.95


