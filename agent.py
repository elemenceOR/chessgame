import numpy as np
import tensorflow as tf
from collections import deque
import random
import chess
from engine import ChessEngine

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # Discount rate
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        
    
    def _build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(self.state_size,)),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dense(self.action_size, activation='linear')
        ])
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, legal_moves):
        if np.random.rand() <= self.epsilon:
            return random.choice(legal_moves) if legal_moves else None
        
        state_tensor = np.reshape(state, [1, self.state_size])
        act_values = self.model.predict(state_tensor, verbose=0)
        
        # Filter predictions for only legal moves
        legal_moves_list = list(legal_moves)
        legal_moves_indices = [self.move_to_index(move) for move in legal_moves_list]
        legal_move_values = [(i, act_values[0][i]) for i in legal_moves_indices]
        
        if not legal_move_values:
            return None
            
        best_move_index = max(legal_move_values, key=lambda x: x[1])[0]
        return self.index_to_move(best_move_index)

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        states = np.zeros((batch_size, self.state_size))
        targets = np.zeros((batch_size, self.action_size))

        for i, (state, action, reward, next_state, done) in enumerate(minibatch):
            target = reward
            if not done:
                next_state_tensor = np.reshape(next_state, [1, self.state_size])
                target = reward + self.gamma * np.amax(self.model.predict(next_state_tensor, verbose=0)[0])
            
            target_f = self.model.predict(np.reshape(state, [1, self.state_size]), verbose=0)
            action_index = self.move_to_index(action)
            target_f[0][action_index] = target
            
            states[i] = state
            targets[i] = target_f[0]

        self.model.fit(states, targets, epochs=1, verbose=0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def move_to_index(self, move):
        """Convert a chess move to a unique index."""
        return move.from_square * 64 + move.to_square

    def index_to_move(self, index):
        """Convert an index back to a chess move."""
        from_square = index // 64
        to_square = index % 64
        return chess.Move(from_square, to_square)

def board_to_state(board):
    """Convert chess board to neural network input state."""
    state = np.zeros(8 * 8 * 12, dtype=np.float32)
    
    piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Calculate piece index (0-5 for white pieces, 6-11 for black pieces)
            piece_idx = piece_types.index(piece.piece_type)
            if not piece.color:  # If black piece
                piece_idx += 6
            
            square_idx = square * 12 + piece_idx
            state[square_idx] = 1
    
    return state

def get_reward(board):
    """Calculate reward based on game state."""
    if board.is_checkmate():
        return 100 if board.turn == chess.BLACK else -100
    elif board.is_stalemate():
        return 0
    
    # Material counting using proper piece types
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    
    white_material = 0
    black_material = 0
    
    for piece_type in piece_values:
        white_material += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        black_material += len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
    
    # Center control
    center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
    white_center = sum(1 for sq in center_squares if board.piece_at(sq) and board.piece_at(sq).color == chess.WHITE)
    black_center = sum(1 for sq in center_squares if board.piece_at(sq) and board.piece_at(sq).color == chess.BLACK)
    
    return (white_material - black_material) + (white_center - black_center) * 0.5

def train_dqn_agent(episodes=1000):
    game = ChessEngine()
    state_size = 8 * 8 * 12  # 8x8 board with 12 piece types
    action_size = 64 * 64    # All possible from-to square combinations
    agent = DQNAgent(state_size, action_size)
    
    for episode in range(episodes):
        game.reset()
        state = board_to_state(game.board)
        total_reward = 0
        move_count = 0
        
        while not game.game_over and move_count < 100:  # Add move limit to prevent infinite games
            legal_moves = list(game.board.legal_moves)
            if not legal_moves:
                break
                
            action = agent.act(state, legal_moves)
            if action is None:
                break
                
            # Make move and get new state
            game.make_move(action)
            next_state = board_to_state(game.board)
            reward = get_reward(game.board)
            done = game.game_over or len(list(game.board.legal_moves)) == 0
            
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            move_count += 1
            
            # Train on a batch of memories
            if len(agent.memory) > 32:
                agent.replay(32)
        
        print(f"Episode {episode + 1}/{episodes} completed with {move_count} moves and reward {total_reward}")

if __name__ == "__main__":
    train_dqn_agent()