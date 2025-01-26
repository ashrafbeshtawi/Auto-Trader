import numpy as np
from neural_network import NeuralNetwork  

class Trader:
    def __init__(self, network=None, initial_fiat=1000.0, initial_btc=0.0):
        """
        Initialize a trader with:
        - Neural network decision maker
        - Wallet balances
        - Trading history
        """
        self.network = network if network else self._create_random_network()
        self.fiat_balance = initial_fiat
        self.btc_balance = initial_btc
        self.total_wealth = initial_fiat
        self.trade_history = []

    def _create_random_network(self):
        """Generate neural network with random architecture"""
        hidden_layers = np.random.choice([0, 1, 2], p=[0.2, 0.5, 0.3])
        layer_sizes = [8]  # Input layer
        for _ in range(hidden_layers):
            layer_sizes.append(np.random.choice([4, 8, 16]))
        layer_sizes.append(1)  # Output layer
        return NeuralNetwork(layer_sizes)

    def decide(self, market_features):
        """
        Process market data through neural network
        Returns: Action value between [-1, 1]
        """
        # Convert features to numpy array in correct order
        feature_order = [
            'sin_month', 'cos_month',
            'sin_doy', 'cos_doy',
            'sin_dow', 'cos_dow',
            'year_scaled', 'fear_greed'
        ]
        inputs = np.array([market_features[k] for k in feature_order], dtype=np.float32)
        return self.network.predict(inputs)

    def execute_trade(self, action, current_price):
        """
        Execute trade based on neural network's decision
        action: Value between -1 (sell all) to 1 (buy all)
        """
        action = np.clip(action, -1.0, 1.0)
        previous_wealth = self.total_wealth
        
        if action > 0:  # Buy BTC
            max_btc_can_buy = self.fiat_balance / current_price
            btc_to_buy = max_btc_can_buy * abs(action)
            self.fiat_balance -= btc_to_buy * current_price
            self.btc_balance += btc_to_buy
        elif action < 0:  # Sell BTC
            btc_to_sell = self.btc_balance * abs(action)
            self.fiat_balance += btc_to_sell * current_price
            self.btc_balance -= btc_to_sell
        
        self.total_wealth = self.fiat_balance + (self.btc_balance * current_price)
        self.trade_history.append({
            'action': action,
            'price': current_price,
            'wealth_change': self.total_wealth - previous_wealth
        })

    def sell_all(self, current_price):
        """Convert all BTC to fiat"""
        self.execute_trade(-1.0, current_price)

    def serialize(self):
        """Convert trader state to serializable format"""
        return {
            'network': self.network.serialize(),
            'fiat': float(self.fiat_balance),
            'btc': float(self.btc_balance),
            'wealth': float(self.total_wealth)
        }

    @classmethod
    def deserialize(cls, data):
        """Recreate trader from serialized data"""
        trader = cls.__new__(cls)
        trader.network = NeuralNetwork.deserialize(data['network'])
        trader.fiat_balance = data['fiat']
        trader.btc_balance = data['btc']
        trader.total_wealth = data['wealth']
        trader.trade_history = []
        return trader

    def __str__(self):
        return (f"Trader: ${self.fiat_balance:.2f} + "
                f"BTC {self.btc_balance:.4f} "
                f"(Total: ${self.total_wealth:.2f})")