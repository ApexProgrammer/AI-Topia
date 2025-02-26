import numpy as np
from ..config import NEURAL_NET_LAYERS, INPUT_SIZE, OUTPUT_SIZE, LEARNING_RATE

class ColonistBrain:
    def __init__(self):
        self.layers = []
        prev_size = INPUT_SIZE
        
        # Initialize weights for each layer
        for layer_size in NEURAL_NET_LAYERS:
            layer = {
                'weights': np.random.randn(prev_size, layer_size) * np.sqrt(2.0/prev_size),
                'bias': np.zeros((1, layer_size))
            }
            self.layers.append(layer)
            prev_size = layer_size
            
        # Output layer
        self.layers.append({
            'weights': np.random.randn(prev_size, OUTPUT_SIZE) * np.sqrt(2.0/prev_size),
            'bias': np.zeros((1, OUTPUT_SIZE))
        })
        
        self.memory = []

    def relu(self, x):
        """ReLU activation function"""
        return np.maximum(0, x)

    def softmax(self, x):
        """Softmax activation function"""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

    def forward(self, x):
        """Forward pass through the network"""
        current_activation = x
        
        # Hidden layers with ReLU
        for layer in self.layers[:-1]:
            z = np.dot(current_activation, layer['weights']) + layer['bias']
            current_activation = self.relu(z)
        
        # Output layer with softmax
        z = np.dot(current_activation, self.layers[-1]['weights']) + self.layers[-1]['bias']
        output = self.softmax(z)
        
        return output

    def decide_action(self, state):
        """Convert state to numpy array and get action prediction with enhanced resource gathering priority"""
        state_array = np.array(state).reshape(1, -1)
        action_probs = self.forward(state_array)
        
        # Extract relevant state information
        colony_resources = state_array[0][5]  # Resource level from state
        has_job = state_array[0][7]  # Job status from state
        energy = state_array[0][3]  # Energy level from state
        happiness = state_array[0][6]  # Happiness level from state
        
        # Critical resource gathering priorities
        if colony_resources < 0.3:  # Less than 30% resources
            action_probs[0][3] *= 2.5  # Significantly increase probability of gathering resources
            if has_job:
                action_probs[0][3] *= 1.5  # Additional boost if already has a job
        elif colony_resources < 0.5:  # Less than 50% resources
            action_probs[0][3] *= 1.8  # Moderately increase gathering probability
        
        # Job seeking behavior
        if not has_job:
            if colony_resources < 0.5:
                action_probs[0][0] *= 2.0  # Double probability of finding job when resources are needed
            else:
                action_probs[0][0] *= 1.5  # Regular job-seeking priority
        
        # Energy management
        if energy < 0.2:  # Very low energy
            action_probs[0][2] *= 2.0  # Double resting probability
            action_probs[0][3] *= 0.3  # Significantly reduce working probability
        elif energy < 0.4:  # Moderately low energy
            action_probs[0][2] *= 1.5  # Increase resting probability
            action_probs[0][3] *= 0.7  # Slightly reduce working probability
        
        # Happiness consideration
        if happiness < 0.4:  # Low happiness
            action_probs[0][4] *= 1.5  # Increase socializing probability
            action_probs[0][5] *= 1.3  # Increase shopping probability
        
        # Normalize probabilities
        action_probs = action_probs / np.sum(action_probs)
        
        # Add small random variation to prevent getting stuck in patterns
        action_probs += np.random.normal(0, 0.05, action_probs.shape)
        action_probs = np.maximum(action_probs, 0)  # Ensure no negative probabilities
        action_probs = action_probs / np.sum(action_probs)  # Renormalize
        
        # Choose action based on modified probabilities
        action = np.random.choice(OUTPUT_SIZE, p=action_probs[0])
        return action

    def remember(self, state, action, reward, next_state):
        """Store experience in memory for training"""
        self.memory.append((state, action, reward, next_state))
        if len(self.memory) > 1000:  # Limit memory size
            self.memory.pop(0)

    def train(self):
        """Simple training step on stored experiences"""
        if len(self.memory) < 32:
            return

        # Sample random batch
        batch_indices = np.random.choice(len(self.memory), size=32, replace=False)
        batch = [self.memory[i] for i in batch_indices]
        
        # Unpack batch
        states = np.array([exp[0] for exp in batch])
        actions = np.array([exp[1] for exp in batch])
        rewards = np.array([exp[2] for exp in batch])
        
        # Simple gradient update
        current_outputs = self.forward(states)
        target_outputs = current_outputs.copy()
        
        # Update the probabilities for the taken actions
        for i in range(len(batch)):
            target_outputs[i, actions[i]] = rewards[i]
        
        # Simple gradient descent update
        error = target_outputs - current_outputs
        self._backward(states, error)

    def _backward(self, inputs, error):
        """Simple backward pass"""
        learning_rate = LEARNING_RATE
        
        # Update output layer
        delta = error
        for layer in reversed(self.layers):
            # Update weights and biases
            layer['weights'] += learning_rate * np.dot(inputs.T, delta)
            layer['bias'] += learning_rate * np.sum(delta, axis=0, keepdims=True)
            
            # Calculate delta for next layer
            delta = np.dot(delta, layer['weights'].T) * (inputs > 0)  # ReLU derivative
            inputs = np.dot(inputs, layer['weights']) + layer['bias']
            inputs = self.relu(inputs)
