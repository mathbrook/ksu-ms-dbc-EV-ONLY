import cantools
from dbc_to_json import cantools_dbc_to_json
from json_to_dbc import cantools_json_to_dbc

# Method to test the generation code that it isnt messing things up
def test_json_gen():
    # Make a json file with the existing DBCs
    cantools_dbc_to_json(db = get_dbc_files(),outfilename="test")

    # Parse the json file and generate a new singular DBC
    cantools_json_to_dbc(input_json="test.json",outfilename="ksu_dbc")

    # Turn the DBC file we made into another json and compare with the first
    mega_dbc=cantools.db.Database()
    with open ('ksu_dbc.dbc', 'r') as newdbc:
        mega_dbc.add_dbc(newdbc)
    cantools_dbc_to_json(db=mega_dbc,outfilename="can_descriptor")

    # Compare their differences
    import difflib
    with open('can_descriptor.json') as file_1:
        file_1_text = file_1.readlines()
    
    with open('test.json') as file_2:
        file_2_text = file_2.readlines()
    
    # Find and print the diff:
    for line in difflib.unified_diff(
            file_1_text, file_2_text, fromfile='file1.txt', tofile='file2.txt', lineterm=''):
                print(line)