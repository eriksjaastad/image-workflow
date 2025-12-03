#!/usr/bin/env python3
"""
Test: Did AI learn anomaly detection or just "pick highest stage"?

Checks cases where Erik chose a LOWER stage (overriding the usual rule).
Did the AI also pick the lower stage in those cases?
"""

import csv
import json
from pathlib import Path

import numpy as np
import torch

# Load model
model_path = Path("data/ai_data/models/ranker_v1.pt")
checkpoint = torch.load(model_path, map_location="cpu")

from train_ranker import RankingModel

model = RankingModel()
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

# Load embeddings
embeddings = {}
cache_file = Path("data/ai_data/cache/processed_images.jsonl")
with open(cache_file) as f:
    for line in f:
        data = json.loads(line)
        img_path = data["image_path"]
        emb_file = Path(data["embedding_file"])
        if emb_file.exists():
            embeddings[img_path] = np.load(emb_file)


# Load training log
log_file = Path("data/training/selection_only_log.csv")

# Find cases where Erik chose LOWER stage
anomaly_cases = []


with open(log_file) as f:
    reader = csv.DictReader(f)

    for row in reader:
        winner_path = row["chosen_path"].strip()
        neg_paths_str = row["neg_paths"].strip()

        try:
            neg_paths = json.loads(neg_paths_str.replace('""', '"'))
        except Exception:
            continue

        # Extract stages
        winner_name = Path(winner_path).name

        # Parse stage from filename
        def get_stage_num(filename):
            if "stage3" in filename:
                return 3
            if "stage2" in filename:
                return 2
            if "stage1.5" in filename:
                return 1.5
            if "stage1" in filename:
                return 1
            return 0

        winner_stage = get_stage_num(winner_name)

        # Check if any loser has HIGHER stage
        for neg_path in neg_paths:
            neg_name = Path(neg_path).name
            neg_stage = get_stage_num(neg_name)

            if neg_stage > winner_stage:
                # FOUND ONE! Erik chose lower stage
                # Find embeddings
                winner_emb = None
                loser_emb = None

                for emb_path, emb in embeddings.items():
                    if Path(emb_path).name == winner_name:
                        winner_emb = emb
                    if Path(emb_path).name == neg_name:
                        loser_emb = emb

                if winner_emb is not None and loser_emb is not None:
                    anomaly_cases.append(
                        {
                            "erik_choice": winner_name,
                            "erik_stage": winner_stage,
                            "rejected": neg_name,
                            "rejected_stage": neg_stage,
                            "winner_emb": winner_emb,
                            "loser_emb": loser_emb,
                        }
                    )


if len(anomaly_cases) == 0:
    pass
else:
    # Test AI on these anomaly cases
    ai_correct = 0
    ai_wrong = 0

    for _i, case in enumerate(anomaly_cases[:20]):  # Show first 20
        winner_emb = torch.from_numpy(case["winner_emb"]).float().unsqueeze(0)
        loser_emb = torch.from_numpy(case["loser_emb"]).float().unsqueeze(0)

        with torch.no_grad():
            winner_score = model(winner_emb).item()
            loser_score = model(loser_emb).item()

        ai_picked_winner = winner_score > loser_score

        if ai_picked_winner:
            ai_correct += 1
            result = "✅ CORRECT"
        else:
            ai_wrong += 1
            result = "❌ WRONG"

    if len(anomaly_cases) > 20:
        pass

    if ai_correct / len(anomaly_cases) > 0.5:
        pass
    else:
        pass
