# src/models/game_state.py


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.hand_state = []
        self.active_pokemon = []
        self.bench_pokemon = []
        self.number_of_cards = None
        self.is_first_turn = True
