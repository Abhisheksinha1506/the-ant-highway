from pathlib import Path
import os
import json
import datetime

# Directions: North, East, South, West
DIRECTIONS = ['N', 'E', 'S', 'W']

def turn_right(current):
    return DIRECTIONS[(DIRECTIONS.index(current) + 1) % 4]

def turn_left(current):
    return DIRECTIONS[(DIRECTIONS.index(current) - 1) % 4]

def move_forward(x, y, direction):
    if direction == 'N': return x, y + 1
    if direction == 'E': return x + 1, y
    if direction == 'S': return x, y - 1
    if direction == 'W': return x - 1, y
    return x, y

def evolve(steps_to_take=200):
    base_dir = os.path.dirname(__file__)
    state_path = os.path.join(base_dir, 'state.json')
    grid_dir = os.path.join(base_dir, 'grid')
    log_path = os.path.join(base_dir, 'ant-log.md')

    if not os.path.exists(state_path):
        state = {"ant": {"x": 0, "y": 0, "direction": "N"}, "grid": {}, "steps": 0}
    else:
        with open(state_path, 'r') as f:
            state = json.load(f)

    ant = state["ant"]
    grid = state["grid"] # { "x,y": 1 } for black, absence for white
    
    for _ in range(steps_to_take):
        pos_key = f"{ant['x']},{ant['y']}"
        current_color = grid.get(pos_key, 0) # 0 = white, 1 = black
        
        if current_color == 0: # White
            ant['direction'] = turn_right(ant['direction'])
            grid[pos_key] = 1 # Flip to black
            # Create file
            cell_file = os.path.join(grid_dir, f"cell_{ant['x']}_{ant['y']}.txt")
            with open(cell_file, 'w') as f:
                f.write("black")
        else: # Black
            ant['direction'] = turn_left(ant['direction'])
            del grid[pos_key] # Flip to white
            # Delete file
            cell_file = os.path.join(grid_dir, f"cell_{ant['x']}_{ant['y']}.txt")
            if os.path.exists(cell_file):
                os.remove(cell_file)
        
        ant['x'], ant['y'] = move_forward(ant['x'], ant['y'], ant['direction'])
        state["steps"] += 1

    # Save state
    state["ant"] = ant
    state["grid"] = grid
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=4)

    # ASCII snapshot
    if grid:
        min_x = min(int(k.split(',')[0]) for k in grid.keys())
        max_x = max(int(k.split(',')[0]) for k in grid.keys())
        min_y = min(int(k.split(',')[1]) for k in grid.keys())
        max_y = max(int(k.split(',')[1]) for k in grid.keys())
    else:
        min_x = max_x = ant['x']
        min_y = max_y = ant['y']

    # Padding
    min_x -= 1; max_x += 1; min_y -= 1; max_y += 1
    
    rows = []
    for y in range(max_y, min_y - 1, -1):
        row = ""
        for x in range(min_x, max_x + 1):
            if x == ant['x'] and y == ant['y']:
                row += 'A' # Ant
            elif grid.get(f"{x},{y}"):
                row += '█'
            else:
                row += ' '
        rows.append(row)
    
    ascii_snapshot = "\n".join(rows)
    date_str = datetime.date.today().isoformat()
    
    with open(log_path, 'a') as f:
        f.write(f"| {state['steps']} | {date_str} |\n```\n{ascii_snapshot}\n``` |\n")

    # Generate human summary
    black_cells = len(grid)
    summary = f"The ant has completed another {steps_to_take} steps, reaching a total of {state['steps']} steps. "
    summary += f"There are currently {black_cells} black tiles on the grid. "
    if state['steps'] > 10000:
        summary += "The ant has entered the 'highway' phase, building a repeating diagonal structure that stretches into infinity."
    else:
        summary += "The ant is currently in its 'chaotic' phase, exploring local space and flipping tiles in a seemingly random dance."

    with open(os.path.join(base_dir, 'summary.txt'), 'w') as f:
        f.write(summary)

    # Update README with latest status
    readme_path = os.path.join(base_dir, 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            content = f.read()
        
        start_marker = "<!-- LATEST_STATUS_START -->"
        end_marker = "<!-- LATEST_STATUS_END -->"
        
        if start_marker in content and end_marker in content:
            parts = content.split(start_marker)
            prefix = parts[0] + start_marker
            suffix = end_marker + parts[1].split(end_marker)[1]
            new_content = f"{prefix}\n> {summary}\n{suffix}"
            
            with open(readme_path, 'w') as f:
                f.write(new_content)


def update_readme(summary):
    readme_path = Path("README.md")
    if not readme_path.exists(): return
    with open(readme_path, 'r') as f:
        content = f.read()
    
    start_marker = "<!-- LATEST_STATUS_START -->"
    end_marker = "<!-- LATEST_STATUS_END -->"
    
    if start_marker in content and end_marker in content:
        parts = content.split(start_marker)
        prefix = parts[0] + start_marker
        suffix = end_marker + parts[1].split(end_marker)[1]
        new_content = f"{prefix}\n*{summary}*\n{suffix}"
        with open(readme_path, 'w') as f:
            f.write(new_content)

if __name__ == "__main__":
    evolve()
