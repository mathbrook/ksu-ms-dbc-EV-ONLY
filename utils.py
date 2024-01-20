import os, sys
import cantools

def get_dbc_files(keyword: str = None) -> cantools.db.Database:
    # Get all the DBC files for parsing and add them together
    try:
        path_name = 'dbc-files'
        file_path = []
        file_count = 0
        for root, dirs, files in os.walk(path_name, topdown=False):
            for name in files:
                if ".dbc" in name or ".DBC" in name:
                    if keyword is not None:
                        if keyword in name:    
                            fp = os.path.join(root, name)
                            file_path.append(fp)
                            file_count += 1
                    else:
                        fp = os.path.join(root, name)
                        file_path.append(fp)
                        file_count += 1  
    except:
        print('failed, no dbc files found.')
        sys.exit(0)
    mega_dbc=cantools.database.Database()
    for filename in file_path:
        with open (filename, 'r') as newdbc:
            mega_dbc.add_dbc(newdbc)

    print('Step 1: found ' + str(file_count) + ' files in the ' + path_name + ' folder')
    return mega_dbc