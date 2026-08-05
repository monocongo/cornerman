# Question Bank — Coding (Blind 75)

**Async take-home use.** The coding interviewer picks **one** problem sized to the candidate's seniority. Never give two problems in one session.

Difficulty labels are LeetCode's. Tier mapping isn't 1:1 — a Medium is fair for a junior if it's a known pattern; a Hard is unusual for anyone below senior.

---

## Junior tier — Easy pattern problems

Give one. Time budget: **45 min**. Optimal expected on second attempt; brute-force accepted if correct on first.

| Topic | Problem | Key concept |
|-------|---------|-------------|
| Array | Two Sum | Hashmap for O(n) |
| Array | Contains Duplicate | Hashset for O(n) |
| Array | Best Time to Buy and Sell Stock | Single-pass min tracking |
| String | Valid Anagram | Char counting or sorting |
| String | Valid Palindrome | Two-pointer |
| String | Valid Parentheses | Stack |
| Linked List | Reverse a Linked List | Iterative or recursive |
| Linked List | Merge Two Sorted Lists | Dummy node pattern |
| Linked List | Linked List Cycle | Fast/slow pointer |
| Tree | Maximum Depth of Binary Tree | DFS or BFS |
| Tree | Same Tree | Recursive comparison |
| Tree | Invert Binary Tree | Recursive swap |
| Tree | Subtree of Another Tree | Recursive check |
| Tree | Lowest Common Ancestor of BST | BST property |
| DP | Climbing Stairs | Fibonacci pattern |
| Binary | Missing Number | XOR or sum trick |
| Binary | Number of 1 Bits | Bit manipulation |

## Mid tier — Medium pattern problems

Give one. Time budget: **45 min**. Optimal expected on first attempt.

| Topic | Problem | Key concept |
|-------|---------|-------------|
| Array | Product of Array Except Self | Prefix/suffix, no division |
| Array | Maximum Subarray | Kadane's |
| Array | 3Sum | Sort + two-pointer |
| Array | Container With Most Water | Two-pointer |
| Array | Find Minimum in Rotated Sorted Array | Modified binary search |
| Array | Search in Rotated Sorted Array | Modified binary search |
| String | Longest Substring Without Repeating Characters | Sliding window |
| String | Longest Palindromic Substring | Expand from center |
| String | Group Anagrams | Hashmap of sorted keys |
| String | Longest Repeating Character Replacement | Sliding window + count |
| DP | Coin Change | Bottom-up DP |
| DP | Longest Increasing Subsequence | O(n log n) with binary search |
| DP | Word Break | DP with set lookup |
| DP | House Robber | Simple DP |
| DP | Unique Paths | Grid DP |
| DP | Jump Game | Greedy |
| Graph | Number of Islands | DFS/BFS on grid |
| Graph | Clone Graph | DFS/BFS with hashmap |
| Graph | Course Schedule | Topological sort / cycle detection |
| Interval | Merge Intervals | Sort + merge |
| Interval | Insert Interval | Linear scan |
| Interval | Non-overlapping Intervals | Greedy by end time |
| Linked List | Remove Nth Node From End of List | Two-pointer |
| Linked List | Reorder List | Split + reverse + merge |
| Matrix | Set Matrix Zeroes | In-place with first row/col |
| Matrix | Spiral Matrix | Boundary tracking |
| Matrix | Rotate Image | Transpose + reverse |
| Matrix | Word Search | DFS with backtracking |
| Tree | Binary Tree Level Order Traversal | BFS |
| Tree | Validate Binary Search Tree | Recursive with bounds |
| Tree | Kth Smallest Element in BST | Inorder traversal |
| Tree | Construct Binary Tree from Preorder and Inorder | Recursive + hashmap |
| Tree | Implement Trie | Trie construction |
| Heap | Top K Frequent Elements | Heap or bucket sort |

## Senior tier — Medium-Hard problems

Give one. Time budget: **60 min**. Optimal expected; interviewer probes complexity tradeoffs and edge handling.

| Topic | Problem | Key concept |
|-------|---------|-------------|
| String | Minimum Window Substring | Sliding window with freq map |
| String | Encode and Decode Strings | Length-prefix encoding |
| DP | Longest Common Subsequence | 2D DP |
| DP | Maximum Product Subarray | Track running max/min |
| Graph | Pacific Atlantic Water Flow | Multi-source DFS |
| Graph | Longest Consecutive Sequence | Hashset with expand |
| Graph | Graph Valid Tree | Union-find or DFS |
| Graph | Number of Connected Components | Union-find |
| Linked List | Merge K Sorted Lists | Heap or divide-and-conquer |
| Tree | Binary Tree Maximum Path Sum | Post-order DFS |
| Tree | Serialize and Deserialize Binary Tree | DFS with sentinel |
| Tree | Word Search II | Trie + DFS |
| Interval | Meeting Rooms II | Heap of end times |

## Staff tier — usually skipped

Real staff/architect loops rarely include a leetcode round. When they do, expect **one Hard with a systems-flavored discussion**, or a data-structure design problem. Time budget: **60 min**. Grading leans heavier on tradeoff articulation than raw correctness.

Candidates: Alien Dictionary, Serialize/Deserialize Binary Tree, Median from Data Stream, Word Search II, Implement LRU Cache (not strictly Blind 75 but a common staff-tier probe).

---

## How to pick

- Match to `dossier.candidate.seniority` first.
- Prefer a problem the candidate's dossier suggests they *haven't* obviously trained for. Frontend engineer's whole stack is React? Don't hand them bit manipulation. Backend engineer working on payments? A DP problem catches whether they can go outside their day-to-day muscle.
- If the JD is heavy on a domain (e.g., search — reach for Trie problems; ranking — reach for heap problems), lean that way.
- **Never give two problems.** One problem, done properly with walkthrough, is the whole signal.
