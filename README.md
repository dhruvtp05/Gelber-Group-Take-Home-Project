# Gelber Group Take Home Project

## Overview
This project implements a manufacturing cost calculator in Python. Given a target product and a list of available products (each with a purchase price and optional manufacturing inputs), the program calculates the minimum cost to produce the target product. The decision for each component is whether to purchase it outright or manufacture it using its inputs, choosing the cheaper option recursively.

## Problem Statement
You are given:
- A target product name (e.g., "teddy bear")
- A list of products, each defined by:
  - Name
  - Purchase price (in dollars and cents, e.g., "12.34")
  - Size (number of inputs, or 0 if no inputs)
  - If size > 0, a list of input products (each with quantity and name)

The goal is to compute the minimum total cost to obtain the target product, where for each product, you can either:
- Buy it directly at its purchase price
- Manufacture it using its inputs (each input's cost multiplied by quantity, plus the product's own manufacturing cost if applicable—wait, actually, the purchase price is for buying, and manufacturing cost is the sum of input costs)

From the code: The purchase price is the cost to buy, and manufacturing cost is the sum of costs of inputs (each input's min cost * quantity).

The program must parse input from stdin (redirected from a file) and output the minimum cost in cents (as an integer).

## Solution Approach
- **Parsing**: Use regular expressions to extract the target product and product definitions from the input. Handle variations like space-separated or comma-separated formats.
- **Algorithm**: Depth-First Search (DFS) with memoization to compute the minimum cost for each product. For each product:
  - If it has no inputs (size 0), cost is its purchase price.
  - Otherwise, cost is the minimum of: purchase price, or sum of (quantity * min_cost(input)) for all inputs.
- **Memoization**: Use a dictionary to cache computed costs to avoid redundant calculations.
- **Output**: Print the minimum cost for the target product in cents.

## Code Structure
- `main.py`: Main script containing all logic.
  - `parse_cents(price_str)`: Converts dollar.cents string to integer cents.
  - `min_cost(product, products, memo)`: Recursive function with memoization to compute min cost.
  - Input parsing: Uses regex to find target and product lines.
  - Main execution: Reads from stdin, parses, computes, prints result.

## How to Run
1. Ensure Python 3 is installed.
2. Run: `python main.py < test_X.txt` (replace X with 1-5 for different test cases).
3. Output: The minimum cost in cents (e.g., 12300 for $123.00).

## Test Cases
- `test_1.txt`: Simple case, expected output 12300.
- `test_2.txt`: Another simple case, expected output 10.
- `test_3.txt` to `test_5.txt`: More complex cases with multiple products and dependencies. Currently, the program returns 0.00 for these (parsing issues need fixing).

## Dependencies
- Python 3.x
- Standard libraries: `sys`, `re`, `collections`

## Notes for Study
- **Parsing Challenges**: Input format varies (spaces vs commas), so regex handles both.
- **Recursion with Memo**: Prevents exponential time by caching results.
- **Cost Calculation**: Always compare buy vs build for each product.
- **Edge Cases**: Products with no inputs, circular dependencies (not handled, assumes acyclic), large inputs.

This implementation passes tests 1 and 2 but needs debugging for 3-5.
