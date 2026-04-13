#!/usr/bin/env python3
"""
Manufacturing cost calculator - find minimum cost to obtain a target product
"""
import sys
import re

products = {}
memo = {}

def parse_cents(s):
    """Convert string price to cents"""
    if s == "null":
        return -1
    try:
        if '.' in s:
            parts = s.split('.')
            whole = int(parts[0]) if parts[0] else 0
            frac_str = parts[1][:2].ljust(2, '0')
            frac = int(frac_str)
            return whole * 100 + frac
        else:
            return int(s) * 100
    except:
        return -1

def min_cost(name):
    """Calculate minimum cost using DFS + memoization"""
    if name in memo:
        return memo[name]
    
    if name not in products:
        return 0
    
    p = products[name]
    
    # If no inputs required, must purchase  
    if not p['inputs']:
        memo[name] = p['price']
        return p['price']
    
    # Calculate build cost
    build_cost = sum(min_cost(inp) for inp in p['inputs'])
    
    # If cannot purchase, must build
    if p['price'] == -1:
        memo[name] = build_cost
        return build_cost
    
    # Otherwise take minimum
    memo[name] = min(build_cost, p['price'])
    return memo[name]

# Read all input and normalize
all_input = sys.stdin.read().strip()

# Parse target and products
# The input format has target first, then product definitions
#Look for the pattern "target_name number,number," which starts the products

# Split by newlines first
lines = all_input.split('\n')

target = ""
all_products_text = ""

if len(lines) >= 1:
    first_line = lines[0]
    
    # Try two strategies:
    # 1. Look for space followed by product (name),price,size,
    match_space = re.search(r' ([^,]+),(-?\d+(?:\.\d+)?|null),(\d+),', first_line)
    
    # 2. Look for price,size pattern preceded by comma
    match_comma = re.search(r',(-?\d+(?:\.\d+)?|null),(\d+),', first_line)
    
    if match_space and match_space.start() < (match_comma.start() if match_comma else float('inf')):
        # Space-prefixed pattern found first
        space_pos = match_space.start()
        target = first_line[:space_pos].strip()
        all_products_text = first_line[space_pos + 1:] + ('\n' + '\n'.join(lines[1:]) if len(lines) > 1 else "")
    elif match_comma:
        # Comma-number-number pattern found, back up to find product name start
        comma_pos = match_comma.start()
        # Go back to find the space before the product name
        name_end = comma_pos
        while name_end > 0 and first_line[name_end - 1] != ' ':
            name_end -= 1
        
        # If we found a space, target is before it
        if name_end > 0:
            while name_end > 0 and first_line[name_end - 1] == ' ':
                name_end -= 1
        
        target = first_line[:name_end].strip()
        all_products_text = first_line[name_end:].strip() + ('\n' + '\n'.join(lines[1:]) if len(lines) > 1 else "")
    else:
        # No products found in first line
        target = first_line
        all_products_text = '\n'.join(lines[1:]) if len(lines) > 1 else ""
else:
    target = all_input
    all_products_text = ""

# Now parse products from all_products_text
# Replace newlines with spaces for easier parsing
all_products_text = all_products_text.replace('\n', ' ')

pos = 0
while pos < len(all_products_text):
    # Skip whitespace/commas
    while pos < len(all_products_text) and all_products_text[pos] in (' ', ','):
        pos += 1
    
    if pos >= len(all_products_text):
        break
    
    # Find product name (until first comma)
    c1 = all_products_text.find(',', pos)
    if c1 == -1:
        break
    
    name = all_products_text[pos:c1].strip()
    pos = c1 + 1
    
    # Skip whitespace
    while pos < len(all_products_text) and all_products_text[pos] in (' ',):
        pos += 1
    
    # Find price (until next comma)
    c2 = all_products_text.find(',', pos)
    if c2 == -1:
        break
    
    price_str = all_products_text[pos:c2].strip()
    pos = c2 + 1
    
    # Skip whitespace
    while pos < len(all_products_text) and all_products_text[pos] in (' ',):
        pos += 1
    
    # Find size (until next comma)
    c3 = all_products_text.find(',', pos)
    if c3 == -1:
        break
    
    size_str = all_products_text[pos:c3].strip()
    pos = c3 + 1
    
    # Skip whitespace
    while pos < len(all_products_text) and all_products_text[pos] in (' ',):
        pos += 1
    
    try:
        price = parse_cents(price_str)
        size = int(size_str)
    except:
        continue
    
    # Read inputs (semicolon-separated)
    inputs = []
    for i in range(size):
        # Find next delimiter (semicolon, space, or comma)
        positions = []
        semi = all_products_text.find(';', pos)
        if semi != -1:
            positions.append(('semi', semi))
        space = all_products_text.find(' ', pos)
        if space != -1:
            positions.append(('space', space))
        comma = all_products_text.find(',', pos)
        if comma != -1:
            positions.append(('comma', comma))
        
        if not positions:
            # End of string
            inp = all_products_text[pos:].strip()
            if inp:
                inputs.append(inp)
            pos = len(all_products_text)
            break
        
        delim_type, delim_pos = min(positions, key=lambda x: x[1])
        
        inp = all_products_text[pos:delim_pos].strip()
        if inp:
            inputs.append(inp)
        
        if delim_type == 'semi':
            pos = delim_pos + 1
        else:
            pos = delim_pos
            break
    
    if name:
        products[name] = {
            'price': price,
            'inputs': inputs
        }

# Calculate result
result = min_cost(target)

# Format output
if result >= 0:
    dollars = result // 100
    cents = result % 100
    print(f"{dollars}.{cents:02d}")
else:
    print("0.00")
