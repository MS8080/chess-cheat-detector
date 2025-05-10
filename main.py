import chess.pgn
import chess.engine
from tkinter import Tk, filedialog
import os
from tkinter import Tk, filedialog
import random  # for simulating move time


def get_pgn_file():
    root = Tk()
    root.lift()  # Bring dialog to front
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(
        title="Select a Chess file",
        filetypes=[("PGN Files", "*.pgn")]
    )
    root.destroy()

    if not file_path:
        print("❌ No file selected.")
        exit()

    return file_path

# === SETTINGS ===
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"  # Replace with your path
ANALYSIS_TIME = 0.1


# === MAIN ANALYSIS FUNCTION ===
def analyze_pgn(pgn_path):
    print(f"\n📂 Loaded file: {pgn_path}")
    with open(pgn_path) as pgn_file:
        game = chess.pgn.read_game(pgn_file)

    board = game.board()
    move_times = []

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    total_moves = 0
    matches = 0

    for move in game.mainline_moves():
        total_moves += 1
        # Optional: simulate/mock time usage per move (replace with real data if available)
        move_time = random.uniform(1, 60)  # mock: random time between 1-60 seconds
        move_times.append(move_time)
        result = engine.analyse(board, chess.engine.Limit(time=ANALYSIS_TIME))
        # Determine move difficulty using top 3 moves
        result_multi = engine.analyse(board, chess.engine.Limit(time=ANALYSIS_TIME), multipv=3)
        scores = [r["score"].white().score(mate_score=10000) for r in result_multi if "score" in r]
        if len(scores) >= 2:
            difficulty_gap = abs(scores[0] - scores[1])
        else:
            difficulty_gap = 0
        move_difficulty = "Easy"
        if difficulty_gap > 150:
            move_difficulty = "Hard"
        elif difficulty_gap > 60:
            move_difficulty = "Medium"
        best_move = result["pv"][0]
        if move == best_move:
            matches += 1
        # Flag if move took long and was exactly best
        if move_time > 30 and move == best_move:
            print(f"⚠️ Suspicious move: took {move_time:.1f}s, matched engine exactly, and was a {move_difficulty} move.")
        print(f"Move {total_moves}: Difficulty = {move_difficulty}, Time = {move_time:.1f}s")
        board.push(move)

    engine.quit()

    accuracy = matches / total_moves * 100
    avg_time = sum(move_times) / len(move_times)
    print(f"\n♟️ Total Moves: {total_moves}")
    print(f"✅ Best Matches: {matches}")
    print(f"🎯 Accuracy: {accuracy:.2f}%")
    print(f"🕒 Average Move Time: {avg_time:.2f} seconds (simulated)")
    if accuracy > 80:
        print("⚠️ Suspicious: High accuracy detected.")
    elif accuracy < 40:
        print("✅ Likely human play.")
    else:
        print("🟡 Inconclusive.")

# === RUN ===
if __name__ == "__main__":
    pgn_path = get_pgn_file()
    analyze_pgn(pgn_path)