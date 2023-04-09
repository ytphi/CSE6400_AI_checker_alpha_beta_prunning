import sys
import copy

def read_input_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        N = int(lines[0].strip())
        MODE = lines[1].strip()
        YOUPLAY = lines[2].strip()
        DEPTH = int(lines[3].strip())
        cell_values = [list(map(int, line.strip().split())) for line in lines[4:4+N]]
        board_state = [list(line.strip()) for line in lines[4+N:]]
    return N, MODE, YOUPLAY, DEPTH, cell_values, board_state

def write_output_file(filename, action, next_board_state):
    with open(filename, 'w') as file:
        file.write("{} {}\n".format(action[0], action[2]))
        for row in next_board_state:
            file.write("".join(row) + "\n")

def heuristic_evaluation(state):
    return state.player_x_score - state.player_o_score

def cutoff_test(state, depth, depth_limit):
    if depth >= depth_limit or state.is_terminal_state():
        return True
    return False

def get_possible_actions(state, player):
    actions = state.get_stake_actions(player) + state.get_raid_actions(player)
    return actions

def minimax(state, depth, depth_limit, player, alpha_beta_pruning=False, alpha=-sys.maxsize, beta=sys.maxsize):
    if cutoff_test(state, depth, depth_limit):
        return heuristic_evaluation(state), None

    if player == 'X':
        max_value, best_action = -sys.maxsize, None
        for action in get_possible_actions(state, player):
            next_state = state.get_next_state(player, action)
            value, _ = minimax(next_state, depth+1, depth_limit, 'O', alpha_beta_pruning, alpha, beta)
            if value > max_value:
                max_value, best_action = value, action
            if alpha_beta_pruning:
                alpha = max(alpha, max_value)
                if alpha >= beta:
                    break
        return max_value, best_action
    else:
        min_value, best_action = sys.maxsize, None
        for action in get_possible_actions(state, player):
            next_state = state.get_next_state(player, action)
            value, _ = minimax(next_state, depth+1, depth_limit, 'X', alpha_beta_pruning, alpha, beta)
            if value < min_value:
                min_value, best_action = value, action
            if alpha_beta_pruning:
                beta = min(beta, min_value)
                if alpha >= beta:
                    break
        return min_value, best_action

class GameState:
        def __init__(self, N, cell_values, board):
            self.N = N
            self.cell_values = cell_values
            self.board = board
            self.player_x_score = self.calculate_player_score('X')
            self.player_o_score = self.calculate_player_score('O')

        def calculate_player_score(self, player):
            score = 0
            for i in range(self.N):
                for j in range(self.N):
                    if self.board[i][j] == player:
                        score += self.cell_values[i][j]
            return score

        def get_stake_actions(self, player):
            actions = []
            for row in range(self.N):
                for col in range(self.N):
                    if self.board[row][col] == '.':
                        actions.append((row, col, 'Stake'))
            return actions

        def get_raid_actions(self, player):
            actions = []
            for row in range(self.N):
                for col in range(self.N):
                    if self.board[row][col] == player:
                        neighbors = self.get_neighbors(row, col)
                        for r, c in neighbors:
                            if self.board[r][c] == '.':
                                actions.append((r, c, 'Raid'))
            return actions

        def get_neighbors(self, row, col):
            neighbors = []
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                r, c = row + dr, col + dc
                if 0 <= r < self.N and 0 <= c < self.N:
                    neighbors.append((r, c))
            return neighbors

        def is_terminal_state(self):
            for row in self.board:
                if '.' in row:
                    return False
            return True

        def get_next_state(self, player, action):
            row, col, move_type = action
            next_board = copy.deepcopy(self.board)
            next_board[row][col] = player
            if move_type == 'Raid':
                neighbors = self.get_neighbors(row, col)
                for r, c in neighbors:
                    if self.board[r][c] == ('X' if player == 'O' else 'O'):
                        next_board[r][c] = player
            return GameState(self.N, self.cell_values, next_board)

def main():
    # Read input file
    input_filename = "input.txt"
    N, MODE, YOUPLAY, DEPTH, cell_values, board_state = read_input_file(input_filename)

    # Initialize game state
    initial_state = GameState(N=N, cell_values=cell_values, board=board_state)


    if MODE == "MINIMAX":
        score, action = minimax(initial_state, 0, DEPTH, YOUPLAY)
    elif MODE == "ALPHABETA":
        score, action = minimax(initial_state, 0, DEPTH, YOUPLAY, True)

    # Get the next state after performing the action
    next_state = initial_state.get_next_state(YOUPLAY, action)

    # Write the output file
    output_filename = "output.txt"
    write_output_file(output_filename, action, next_state.board)

if __name__ == "__main__":
    main()
