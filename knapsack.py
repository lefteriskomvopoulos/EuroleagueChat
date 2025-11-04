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


# all_items = [
#     {'name': 'Laptop', 'weight': 3, 'value': 2000, 'category': 'electronics'},
#     {'name': 'Camera', 'weight': 2, 'value': 1500, 'category': 'electronics'},
#     {'name': 'Headphones', 'weight': 1, 'value': 300, 'category': 'electronics'},
#     {'name': 'Jacket', 'weight': 2, 'value': 150, 'category': 'clothing'},
#     {'name': 'Shoes', 'weight': 1, 'value': 80, 'category': 'clothing'},
#     {'name': 'Book 1', 'weight': 1, 'value': 40, 'category': 'books'},
#     {'name': 'Book 2', 'weight': 1, 'value': 35, 'category': 'books'}
# ]

# total_capacity = 6
# category_limits = {
#     'electronics': 2,
#     'clothing': 1,
#     'books': 3
# }
# max_val, final_items = knapsack_multi_category(all_items, category_limits, total_capacity)

# print(max_val)
# print(final_items)

# values = [60, 100, 120, 150, 130]
# weights = [10, 20, 30, 40, 50]
# W = 60
# K = 3
    
# max_value, items = knapSack(W, K, weights, values)
    
# print(max_val)
# print(items)

### Simple KnapSack ###
# values = df_values.groupby('player_name')[['player_performance', 'player_credits']].mean().reset_index().to_dict(orient='records')
# values = {value['player_name']: {'performance': int(value['player_performance']), 'credits': int(value['player_credits']), 'position': int(value['player_position'])} for value in values}
# players = []
# credits = []
# performances = []
# for key, value in values.items():
#     players.append(key)
#     credits.append(value['credits'])
#     performances.append(value['performance'])
# results = knapSack(max_credits, max_players, credits, performances)
# results = {players[j]: {'credits': credits[j], 'performance': performances[j]} for j in results[1]}