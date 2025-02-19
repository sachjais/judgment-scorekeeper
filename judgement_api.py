from flask import Flask, request, jsonify
from flask_cors import CORS

import random

app = Flask(__name__)
CORS(app)  # This allows OpenAI to communicate with the API


game_state = {}

def select_trump():
    """Randomly selects a trump suit."""
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    return random.choice(suits)

def determine_rounds(num_players):
    """Determines the number of rounds based on the number of players."""
    if num_players == 3:
        return 5
    elif num_players in [4, 5]:
        return 4
    elif num_players == 6:
        return 3
    else:
        return None

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    players = [p.strip() for p in data.get("players").split(",")]
    num_rounds = determine_rounds(len(players))
    
    if not num_rounds:
        return jsonify({"error": "Invalid number of players! Must be between 3-6."})

    game_state["players"] = players
    game_state["scores"] = {player: 0 for player in players}
    game_state["round"] = 1
    game_state["max_rounds"] = num_rounds

    return jsonify({
        "message": f"Game started with {len(players)} players!",
        "round": 1,
        "trump_suit": select_trump(),
        "cards_per_round": 1
    })

@app.route('/set_bids', methods=['POST'])
def set_bids():
    data = request.json
    bids = list(map(int, data.get("bids").split(",")))

    if len(bids) != len(game_state["players"]):
        return jsonify({"error": "Number of bids must match number of players."})

    game_state["bids"] = dict(zip(game_state["players"], bids))

    return jsonify({"message": "Bids recorded!", "bids": game_state["bids"]})

@app.route('/record_tricks', methods=['POST'])
def record_tricks():
    data = request.json
    tricks_won = list(map(int, data.get("tricks").split(",")))

    if len(tricks_won) != len(game_state["players"]):
        return jsonify({"error": "Number of tricks must match number of players."})

    players = game_state["players"]
    scores = game_state["scores"]
    bids = game_state.get("bids", {})

    for i, player in enumerate(players):
        if bids[player] == tricks_won[i]:  # Successful bid
            scores[player] += 10 + tricks_won[i]
        else:
            scores[player] -= abs(bids[player] - tricks_won[i])

    game_state["scores"] = scores

    # Advance round
    game_state["round"] += 1
    if game_state["round"] > game_state["max_rounds"]:
        return jsonify({"message": "Game over!", "final_scores": game_state["scores"]})

    return jsonify({
        "message": "Scores updated!",
        "scores": game_state["scores"],
        "next_round": game_state["round"],
        "trump_suit": select_trump(),
        "cards_per_round": game_state["round"]
    })

@app.route('/show_scores', methods=['GET'])
def show_scores():
    return jsonify({"scores": game_state.get("scores", {})})

@app.route('/')
def home():
    return jsonify({"message": "Judgment Score Keeper API is running!"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
