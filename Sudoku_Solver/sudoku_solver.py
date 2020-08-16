#!/usr/bin/python3
"""
Retrieved from: https://github.com/KleinSamuel/sudoku-solver
"""
import sys
'''
# strings for example sudokus where .=0
easy1 = ".94...13..............76..2.8..1.....32.........2...6.....5.4.......8..7..63.4..8"
hard1 = ".....6....59.....82....8....45........3........6..3.54...325..6.................."
test1 = "070006000900000041008009050090007002003000800400800010080300900160000007000500080"
'''
rows = "ABCDEFGHI"
columns = "123456789"

# Create combinations of given rows and columns
def combine(row, col):
    out = []
    for r in row:
        for c in col:
            out.append(r+c)
    return out

# List of all cells with respective name; 0:0 = A1; 8:8 = I9;
cells  = combine(rows, columns)

# Lists of all row, column and block combinations
comb_1 = []
for c in columns:
    comb_1.append(combine(rows, c))
comb_2 = []
for r in rows:
    comb_1.append(combine(r, columns))
comb_3 = []
for i in range(0,9,3):
    r = rows[i:i+3]
    for j in range(0,9,3):
        c = columns[j:j+3]
        comb_3.append(combine(r, c))

# Row, column and block combinations concatenated into list
valuesToCompare = (comb_1 + comb_2 + comb_3)

# Dict with cellname as key and name of row, col, block this cell is in as value
comb_dict = {}
for cell in cells:
    tmp = []
    for comb in valuesToCompare:
        if cell in comb:
            tmp.append(comb)
    comb_dict[cell] = tmp

# Set with cellname as key and unique set of cells of row, col, block this cell is in
comb_set = {}
for cell in cells:
    comb_set[cell] = set(sum(comb_dict[cell],[]))-set([cell])

# Create dict from sudoku string with cellname as key and list of possible numbers as value
def create_dict_from_sudoku_string(grid):
    tmp_dict = {}
    for cell in cells:
        tmp_dict[cell] = columns
    for cellname,numbers in create_dict_from_string(grid).items():
        if numbers in columns and not find_values(tmp_dict, cellname, numbers):
            return False
    return tmp_dict

# Creates a dic t from a string where key is cellname and value is cell value
def create_dict_from_string(grid):
    out = {}
    for i in range(0,len(grid)):
        out[cells[i]] = grid[i]
    return out

# Creates new list with all possible numbers for a cellname
def find_values(tmp_dict, cellname, numbers):
    tmp = tmp_dict[cellname].replace(numbers, "")
    if all(remove_impossible_moves(tmp_dict, cellname, numbers_2) for numbers_2 in tmp):
        return tmp_dict
    else:
        return False

# Generates a string from a sudoku dict
def generate_string_from_sudoku(sudoku):
    output = ""
    for row in rows:
        for col in columns:
            output += str(sudoku[row+col])
    return output

# remove numbers from list which are contained in the same row, col or block
def remove_impossible_moves(tmp_dict, cellname, numbers):
    if numbers not in tmp_dict[cellname]:
        return tmp_dict
    tmp_dict[cellname] = tmp_dict[cellname].replace(numbers,'')
    if len(tmp_dict[cellname]) == 0:
        return False
    elif len(tmp_dict[cellname]) == 1:
        numbers2 = tmp_dict[cellname]
        if not all(remove_impossible_moves(tmp_dict, cellname2, numbers2) for cellname2 in comb_set[cellname]):
            return False
    for cells in comb_dict[cellname]:
        f = [cellname for cellname in cells if numbers in tmp_dict[cellname]]
        if len(f) == 0:
            return False
        elif len(f) == 1:
            if not find_values(tmp_dict, f[0], numbers):
                return False
    return tmp_dict
'''
# Print formatted sudoku
def printSudoku(tmp_dict):
    line = "+-------+-------+-------+"
    print(line)
    for r in rows:
        sys.stdout.write("| ")
        for c in columns:
            sys.stdout.write(tmp_dict[r+c]+" ")
            if int(c)%3 == 0:
                sys.stdout.write("| ")
            if c == "9":
                print("")
        if r in "CF": print(line)
    print(line)
'''
# Solve given sudoku string
def solve_sudoku(sudoku_string):
    return recursive_solve(create_dict_from_sudoku_string(sudoku_string))

# To recursively Solve
def recursive_solve(tmp_dict):
    if tmp_dict is False:
        return False
    # check if every cell only has one possible number -> sudoku is solved and can be returned
    return_flag = True
    for cellname in cells:
        if len(tmp_dict[cellname]) != 1:
            return_flag = False
            break
    if return_flag:
        return tmp_dict
    # get cell with fewest possible numbers
    tmp_cell = None
    tmp_counter = 100
    for cellname in cells:
        if len(tmp_dict[cellname]) > 1:
            if len(tmp_dict[cellname]) < tmp_counter:
                tmp_counter = len(tmp_dict[cellname])
                tmp_cell = cellname
    # iterate each possible number in this cell and call recursive function
    return return_one_item(recursive_solve(find_values(tmp_dict.copy(), tmp_cell, move)) for move in tmp_dict[tmp_cell])

# Return the first item in dict and False if no items exist
def return_one_item(tmp_dict):
    for item in tmp_dict:
        if item:
            return item
    return False

