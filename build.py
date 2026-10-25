#!/usr/bin/env python3
"""Bundle problems/*/*.json into docs/problems.json (served by both GitHub Pages and server.py)."""
import glob, json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
probs = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(ROOT, "problems", "*", "*.json")))]
json.dump(probs, open(os.path.join(ROOT, "docs", "problems.json"), "w"))
print(len(probs), "problems")
