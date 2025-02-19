from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Store game state globally
game_state = {}

class JudgmentGame:
    def __init__(self, player_names):
        self.num_players = len(player_names)
        self.players = {name.strip(): {"bid": 0, "tricks_won": 0, "score": 0} for name in player_names}
        self.round = 1
        self.trump_suit = "Spades"
        self.dealer_index = 0
        self.max_rounds = 52 // self.num_players  # Maximum rounds before deck is exhausted
        self.cards_per_round = 1  # First round starts with 1 card

    def set_bids(self, bids):
        for i, bid in enumerate(bids):
            player_name = list(self.players.keys())[i]
            self.players[player_name]["bid"] = bid

    def record_tricks_won(self, tricks):
        for i, tricks_won in enumerate(tricks):
            player_name = list(self.players.keys())[i]
            self.players[player_name]["tricks_won"] = tricks_won
            if tricks_won == self.players[player_name]["bid"]:
                self.players[player_name]["score"] += 10 + tricks_won  # Correct bid
            else:
                self.players[player_name]["score"] += 0  # Incorrect bid

    def next_round(self):
        if self.round < self.max_rounds:
            self.round += 1
            self.cards_per_round += 1  # Increase cards dealt per round
            self.trump_suit = ["Spades", "Hearts", "Clubs", "Diamonds"][self.round % 4]  # Rotate trump
            self.dealer_index = (self.dealer_index + 1) % self.num_players  # Rotate dealer
            return {
                "round": self.round,
                "trump_suit": self.trump_suit,
                "dealer": list(self.players.keys())[self.dealer_index],
                "cards_per_round": self.cards_per_round
            }
        return "Game over."

    def get_scores(self):
        return {player: self.players[player]["score"] for player in self.players}

@app.route('/')
def home():
    return jsonify({"message": "Judgment Score Keeper API is running!"})

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    player_names = [name.strip() for name in data.get("players").split(",")]
    global game_state
    game_state["game"] = JudgmentGame(player_names)
    first_dealer = player_names[0]
    return jsonify({
        "response": f"Game started with {len(player_names)} players. Round 1 begins.",
        "trump_suit": "Spades",
        "first_dealer": first_dealer,
        "cards_per_round": 1
    })

@app.route('/set_bids', methods=['POST'])
def set_bids():
    data = request.json
    bids = list(map(int, data.get("bids").split(",")))
    game_state["game"].set_bids(bids)
    return jsonify({"response": "Bids recorded. Start playing!"})

@app.route('/record_tricks', methods=['POST'])
def record_tricks():
    data = request.json
    tricks = list(map(int, data.get("tricks").split(",")))
    game_state["game"].record_tricks_won(tricks)
    next_round_info = game_state["game"].next_round()
    return jsonify({"response": "Scores updated.", "scores": game_state["game"].get_scores(), "next_round": next_round_info})

@app.route('/show_scores', methods=['GET'])
def show_scores():
    return jsonify({"response": game_state["game"].get_scores()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
