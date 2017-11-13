assignments = []






def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [x+y for x in A for y in B]
rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# Create another unit section for the diagonals. To remove, get rid of call in 'unitlist'
diagonal_units = [[r+c for r,c in zip(rows,cols)],[r+c for r,c in zip(rows,reversed(cols))]]

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def intersect(a, b):
    return list(set(a) & set(b))

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # iterate through all possible units in the puzzle. If there are 2 boxes with the same value and are of length 2
    # store them as a tuple in the twins list. Make sure to not store the same pair twice
    twins = []
    for u in unitlist:
        for s in u:
            for o in u:
                if s != o and len(values[s]) == 2 and values[s] == values[o]:
                     if not (s,o) in twins and not (o,s) in twins:
                         twins.append((s,o))

    # Eliminate the naked twins as possibilities for their peers
    # iterate through all twin pairings, and check their peers
    # If not one of the boxes in the pair, check if any values from the pair are in the box, and remove them
    for t in twins:
        twin_peers = intersect(peers[t[0]],peers[t[1]])
        for p in twin_peers:
            if not p == t[0] and not p == t[1]:
                if values[t[0]][0] in values[p]:
                    if values[t[0]][1] in values[p]:
                        assign_value(values, p, values[p].replace(values[t[0]],''))
                    else :
                        assign_value(values, p, values[p].replace(values[t[0]][0],''))
                elif values[t[0]][1] in values[p]:
                    assign_value(values, p, values[p].replace(values[t[0]][1],''))

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    #Make sure grid is proper length
    assert len(grid) == 81
    sudoko_dict = dict()

    #Take a dictionary, and put each character 'c' in the given grid in each box 'i'.
    for c, i in zip(grid, boxes):
        if c == '.':
            sudoko_dict[i] = '123456789'
        else:
            sudoko_dict[i] = c

    return sudoko_dict

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    # Get the max width for a box
    box_width = 1 + max(len(values[box]) for box in boxes)

    # Make the segment between every 3 rows
    line_space = '+'.join(['-' * box_width * 3] * 3)

    # Go through the rows and print the values, and print the line_space after every 3rd row. and put a | after every
    # 3rd column
    for r in rows:
        # r+c will give every box for a respective row r.
        print(''.join(values[r + c].center(box_width) + ('|' if c in '36' else ' ') for c in cols))
        if r in 'CF':
            print(line_space)

    pass

def eliminate(values):
    #For each grid element c, check if it's pre-solved. If not, fill in the box with all digits
    solved = dict()
    for k in values:
        if len(values[k]) == 1:
            solved[k] = values[k]

    for k in solved:
        for p in peers[k]:
            assign_value(values,p,values[p].replace(solved[k],''))

    return values

def only_choice(values):
    for u in unitlist:
        for num in '123456789':
            boxes = [box for box in u if num in values[box]]
            if len(boxes) == 1:
                assign_value(values,boxes[0],num)

    return values


def reduce_puzzle(values):
    stalled = False

    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        eliminate(values)

        # Your code here: Use the Only Choice Strategy
        only_choice(values)

        #Use Twin Peaks Strategy
        naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values

def search(values):
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    min_options = None

    for box in values:
        if len(values[box]) > 1:
            if min_options == None:
                min_options = box
            elif len(values[box]) < len(values[min_options]):
                min_options = box

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!

    for num in values[min_options]:
        depth_puzzle = values.copy()
        depth_puzzle[min_options] = num
        answer = search(depth_puzzle)
        if answer:
            return answer

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
