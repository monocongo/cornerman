#!/usr/bin/env python3
"""Build blind75.json by parsing the jaimin-bariya/blind-75-leetcode README.

Run with:
    python build_blind75.py

Writes blind75.json next to this script.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

README_URL = "https://raw.githubusercontent.com/jaimin-bariya/blind-75-leetcode/main/README.md"

DIFFICULTY: dict[str, str] = {
    "Two Sum": "easy",
    "Best Time to Buy and Sell Stock": "easy",
    "Contains Duplicate": "easy",
    "Product of Array Except Self": "medium",
    "Maximum Subarray": "medium",
    "Maximum Product Subarray": "medium",
    "Find Minimum in Rotated Sorted Array": "medium",
    "Search in Rotated Sorted Array": "medium",
    "3Sum": "medium",
    "Container With Most Water": "medium",
    "Sum of Two Integers": "medium",
    "Number of 1 Bits": "easy",
    "Counting Bits": "easy",
    "Missing Number": "easy",
    "Reverse Bits": "easy",
    "Climbing Stairs": "easy",
    "Coin Change": "medium",
    "Longest Increasing Subsequence": "medium",
    "Longest Common Subsequence": "medium",
    "Word Break": "medium",
    "Combination Sum": "medium",
    "House Robber": "medium",
    "House Robber II": "medium",
    "Decode Ways": "medium",
    "Unique Paths": "medium",
    "Jump Game": "medium",
    "Clone Graph": "medium",
    "Course Schedule": "medium",
    "Pacific Atlantic Water Flow": "medium",
    "Number of Islands": "medium",
    "Longest Consecutive Sequence": "medium",
    "Alien Dictionary": "hard",
    "Graph Valid Tree": "medium",
    "Number of Connected Components in an Undirected Graph": "medium",
    "Insert Interval": "medium",
    "Merge Intervals": "medium",
    "Non-overlapping Intervals": "medium",
    "Meeting Rooms": "easy",
    "Meeting Rooms II": "medium",
    "Reverse Linked List": "easy",
    "Detect Cycle in a Linked List": "easy",
    "Merge Two Sorted Lists": "easy",
    "Merge k Sorted Lists": "hard",
    "Remove Nth Node From End of List": "medium",
    "Reorder List": "medium",
    "Set Matrix Zeroes": "medium",
    "Spiral Matrix": "medium",
    "Rotate Image": "medium",
    "Word Search": "medium",
    "Longest Substring Without Repeating Characters": "medium",
    "Longest Repeating Character Replacement": "medium",
    "Minimum Window Substring": "hard",
    "Valid Anagram": "easy",
    "Group Anagrams": "medium",
    "Valid Parentheses": "easy",
    "Valid Palindrome": "easy",
    "Longest Palindromic Substring": "medium",
    "Palindromic Substrings": "medium",
    "Encode and Decode Strings": "medium",
    "Maximum Depth of Binary Tree": "easy",
    "Same Tree": "easy",
    "Invert Binary Tree": "easy",
    "Binary Tree Maximum Path Sum": "hard",
    "Binary Tree Level Order Traversal": "medium",
    "Serialize and Deserialize Binary Tree": "hard",
    "Subtree of Another Tree": "easy",
    "Construct Binary Tree from Preorder and Inorder Traversal": "medium",
    "Validate Binary Search Tree": "medium",
    "Kth Smallest Element in a BST": "medium",
    "Lowest Common Ancestor of a Binary Search Tree": "easy",
    "Implement Trie (Prefix Tree)": "medium",
}

ITEM_RE = re.compile(r"- \[[ x]\] \[([^\]]+)\]\(([^)]+)\)")


def fetch_readme(local_path: Path | None = None) -> str:
    if local_path and local_path.exists():
        return local_path.read_text()
    with urllib.request.urlopen(README_URL) as resp:
        return resp.read().decode("utf-8")


def parse(readme: str) -> list[dict]:
    problems: list[dict] = []
    current_category = None
    for line in readme.splitlines():
        line = line.strip()
        if line.startswith("## "):
            current_category = line[3:].strip()
            continue
        m = ITEM_RE.match(line)
        if not m or current_category is None:
            continue
        name = m.group(1)
        url = m.group(2)
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        difficulty = DIFFICULTY.get(name)
        if difficulty is None:
            print(f"warning: no difficulty mapping for {name!r}", file=sys.stderr)
            difficulty = "medium"
        problems.append(
            {
                "id": slug,
                "name": name,
                "category": current_category,
                "difficulty": difficulty,
                "url": url,
            }
        )
    return problems


def main() -> int:
    here = Path(__file__).parent
    local_readme = here / "blind75-source.md"
    readme = fetch_readme(local_readme if local_readme.exists() else None)
    problems = parse(readme)
    out = here / "blind75.json"
    out.write_text(json.dumps(problems, indent=2) + "\n")
    by_diff = {"easy": 0, "medium": 0, "hard": 0}
    for p in problems:
        by_diff[p["difficulty"]] += 1
    print(f"wrote {len(problems)} problems to {out}")
    print(f"  easy={by_diff['easy']} medium={by_diff['medium']} hard={by_diff['hard']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
