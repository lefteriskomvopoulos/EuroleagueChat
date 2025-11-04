def knapSack(W, K, weights, values):

    n = len(values)
    dp = [[[0 for _ in range(K + 1)] for _ in range(W + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(1, W + 1):
            for k in range(1, K + 1):
                if weights[i-1] <= w:
                    value_if_included = values[i-1] + dp[i-1][w - weights[i-1]][k-1]
                    value_if_excluded = dp[i-1][w][k]
                    dp[i][w][k] = max(value_if_included, value_if_excluded)
                else:
                    dp[i][w][k] = dp[i-1][w][k]
    
    max_value = 0
    for w in range(W + 1):
        for k in range(K + 1):
            max_value = max(max_value, dp[n][w][k])
            
    selected_items = []
    w = W
    k = K
    for i in range(n, 0, -1):
        if dp[i][w][k] == dp[i-1][w][k]:
            continue
        else:
            selected_items.append(i-1)
            w -= weights[i-1]
            k -= 1
    
    return max_value, selected_items

import json

def knapsack_multi_category(items, cat_limits, capacity):

    memo = {}
    cat_names = list(cat_limits.keys())
    cat_to_index = {cat: i for i, cat in enumerate(cat_names)}
    
    initial_slots = tuple(cat_limits[name] for name in cat_names)

    def solve(i, w_left, remaining_slots_tuple):

        if i == len(items) or w_left == 0:
            return (0, [])

        state = (i, w_left, remaining_slots_tuple)
        if state in memo:
            return memo[state]

        item = items[i]
        item_weight = item['weight']
        item_value = item['value']
        item_category = item['category']
        
        val_skip, items_skip = solve(i + 1, w_left, remaining_slots_tuple)
        val_take, items_take = (0, [])
        
        if item_weight <= w_left:

            cat_index = cat_to_index[item_category]
            
            if remaining_slots_tuple[cat_index] > 0:
                
                new_slots_list = list(remaining_slots_tuple)
                new_slots_list[cat_index] -= 1
                new_slots_tuple = tuple(new_slots_list)
                
                val_rest, items_rest = solve(i + 1, w_left - item_weight, new_slots_tuple)
                
                val_take = item_value + val_rest
                items_take = [item] + items_rest

        if val_take > val_skip:
            memo[state] = (val_take, items_take)
            return (val_take, items_take)
        else:
            memo[state] = (val_skip, items_skip)
            return (val_skip, items_skip)

    max_value, chosen_items = solve(0, capacity, initial_slots)
    return max_value, chosen_items