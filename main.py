from flask import Flask, request, jsonify

app = Flask(__name__)

# Store game state globally
game_state = {}

class JudgmentGame:
    def __init__(self, num_players):
        self.num_players = num_players
        self.players = {f"Player {i+1}": {"bid": 0, "tricks_won": 0, "score": 0} for i in range(num_players)}
        self.round = 1
        self.trump_suit = "Spades"
        self.dealer_index = 0
        self.max_rounds = {3: 17, 4: 13, 5: 10, 6: 8}[num_players]

    def set_bids(self, bids):
        for i, bid in enumerate(bids):
            self.players[f"Player {i+1}"]["bid"] = bid

    def record_tricks_won(self, tricks):
        for i, tricks_won in enumerate(tricks):
            self.players[f"Player {i+1}"]["tricks_won"] = tricks_won
            if tricks_won == self.players[f"Player {i+1}"]["bid"]:
                self.players[f"Player {i+1}"]["score"] += 10 + tricks_won  # Correct bid
            else:
                self.players[f"Player {i+1}"]["score"] += 0  # Incorrect bid

    def next_round(self):
        if self.round < self.max_rounds:
            self.round += 1
            self.trump_suit = ["Spades", "Hearts", "Clubs", "Diamonds"][self.round % 4]
            self.dealer_index = (self.dealer_index + 1) % self.num_players
            return f"Round {self.round} begins. Trump suit is {self.trump_suit}. Player {self.dealer_index+1} deals first."
        return "Game over."

    def get_scores(self):
        return {player: self.players[player]["score"] for player in self.players}

@app.route('/')
def home():
    return jsonify({"message": "Judgment Score Keeper API is running!"})

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    num_players = data.get("num_players")
    global game_state
    game_state["game"] = JudgmentGame(num_players)
    return jsonify({"response": f"Game started with {num_players} players. Round 1 begins. Trump suit is Spades. Player 1 deals first."})

@app.route('/set_bids', methods=['POST'])
def set_bids():
    data = request.json
    bids = data.get("bids")
    game_state["game"].set_bids(bids)
    return jsonify({"response": "Bids recorded. Start playing!"})

@app.route('/record_tricks', methods=['POST'])
def record_tricks():
    data = request.json
    tricks = data.get("tricks")
    game_state["game"].record_tricks_won(tricks)
    return jsonify({"response": "Scores updated.", "scores": game_state["game"].get_scores(), "next_round": game_state["game"].next_round()})

@app.route('/show_scores', methods=['GET'])
def show_scores():
    return jsonify({"response": game_state["game"].get_scores()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
