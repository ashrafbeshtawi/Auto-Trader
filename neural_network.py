import numpy as np
import json

class DenseLayer:
    def __init__(self, input_size, output_size, activation='relu'):
        self.weights = np.random.randn(input_size, output_size) * 0.1
        self.activation = activation
        
    def forward(self, x):
        z = np.dot(x, self.weights)
        return self._apply_activation(z)
    
    def _apply_activation(self, z):
        if self.activation == 'relu':
            return np.maximum(0, z)
        elif self.activation == 'tanh':
            return np.tanh(z)
        return z
    
    def __str__(self):
        return f"DenseLayer({self.weights.shape[0]}→{self.weights.shape[1]}, {self.activation})"

class NeuralNetwork:
    def __init__(self, layer_sizes=[8, 4, 1]):
        """
        Initialize a neural network with variable architecture
        Example: layer_sizes = [8, 16, 8, 1] creates:
        - Input: 8 nodes
        - Hidden: 16 nodes (relu)
        - Hidden: 8 nodes (relu)
        - Output: 1 node (tanh)
        """
        self.layers = []
        for i in range(len(layer_sizes)-1):
            activation = 'tanh' if i == len(layer_sizes)-2 else 'relu'
            self.layers.append(
                DenseLayer(layer_sizes[i], layer_sizes[i+1], activation)
            )
    
    def predict(self, x):
        """
        Process input through the network
        Returns: float between -1 and 1
        """
        if not isinstance(x, np.ndarray):
            x = np.array(x, dtype=np.float32)
            
        for layer in self.layers:
            x = layer.forward(x)
        return x.item()  # Return scalar value
    
    def mutate(self, mutation_rate=0.1, mutation_scale=0.2):
        """
        Randomly mutate network weights
        mutation_rate: Probability of weight change
        mutation_scale: Magnitude of changes (std dev of normal distribution)
        """
        for layer in self.layers:
            if np.random.random() < mutation_rate:
                mutation = np.random.normal(
                    scale=mutation_scale,
                    size=layer.weights.shape
                )
                layer.weights += mutation
    
    def serialize(self):
        """Convert network to JSON-serializable format"""
        return {
            'architecture': self.get_architecture(),
            'weights': [layer.weights.tolist() for layer in self.layers],
            'activations': [layer.activation for layer in self.layers]
        }
    
    def get_architecture(self):
        """Get layer architecture as list of sizes"""
        arch = [layer.weights.shape[0] for layer in self.layers]
        arch.append(self.layers[-1].weights.shape[1])
        return arch
    
    @classmethod
    def deserialize(cls, data):
        """Create network from serialized data"""
        network = cls.__new__(cls)
        network.layers = []
        
        # Reconstruct layers from serialized data
        for i in range(len(data['architecture'])-1):
            input_size = data['architecture'][i]
            output_size = data['architecture'][i+1]
            activation = data['activations'][i]
            
            layer = DenseLayer(input_size, output_size, activation)
            layer.weights = np.array(data['weights'][i])
            network.layers.append(layer)
            
        return network
    
    def __str__(self):
        arch = "→".join(map(str, self.get_architecture()))
        return f"NeuralNetwork({arch})"