from typing import Dict

def pretty_output(var: Dict, filename: str='tmp.json'):
    """Output the dictionary into file

    Args:
        var (Dict): Collection of variables for different servers
        filename (str, optional): Output file name, defaults to 'tmp.json'.
    """
    with open(filename, 'w', encoding='utf-8') as fp:
        idx = 0 # Count the number of loops
        fp.write('{\n')
        for key in var.keys():
            idx += 1
            
            # server id
            fp.write("    " * 1 + f"\"{key}\": {{\n")
            
            # activated
            fp.write("    " * 2 + f"\"activated\": {var[key]['activated']},\n")
            
            # bully
            fp.write("    " * 2 + f"\"bully\": ")
            if len(var[key]['bully']) == 0:
                fp.write("{},\n")
            else:
                fp.write("{\n")
                for id, val in var[key]['bully'].items():
                    fp.write("    " * 3 + f"{id}: {val},\n")
                fp.write("    " * 2 + '},\n')
            
            # ctx
            fp.write("    " * 2 + f"\"ctx\": {var[key]['ctx']},\n")
            
            # object
            fp.write("    " * 2 + "\"log\": ")
            if len(var[key]['log']) == 0:
                fp.write('[],\n')
            else:
                fp.write('[\n')
                for record in var[key]['log']:
                    fp.write("    " * 3 + str(record).replace('*', '').replace('`', '') + ("" if record == var[key]['log'][-1] else ',') + '\n')
                fp.write("    " * 2 + '],\n')
            
            # playing
            fp.write("    " * 2 + f"\"playing\": {var[key]['playing']},\n")
            
            # queue
            fp.write("    " * 2 + "\"queue\": ")
            if len(var[key]['queue']) == 0:
                fp.write('[],\n')
            else:
                fp.write('[\n')
                tmp = 0
                for record in var[key]['queue']:
                    tmp += 1
                    fp.write("    " * 3 + f"\"{record}\"" + ('' if tmp == len(var[key]['queue']) else ',') + '\n')
                fp.write("    " * 2 + ']\n')
            
            fp.write('    ' * 1 + '}' + ('' if idx == len(var.keys()) else ',') + '\n')
        fp.write('}')


def pretty_print(var: dict):
    """Print out the dictionary with formatting

    Args:
        var (dict): Collection of variable for different servers
    """
    idx = 0 # Count the number of loops
    print("{")
    for key in var.keys():
        idx += 1
        
        # server id
        print("    " * 1 + f"\"{key}\": {{")
        
        # activated
        print("    " * 2 + f"\"activated\": {var[key]['activated']},")
        
        # bully
        print("    " * 2 + f"\"bully\": ", end='')
        if len(var[key]['bully']) == 0:
            print("{},")
        else:
            print("{")
            for id, val in var[key]['bully'].items():
                print("    " * 3 + f"{id}: {val},")
            print("    " * 2 + '},')
        
        # ctx
        print("    " * 2 + f"\"ctx\": {var[key]['ctx']},")
        
        # log
        print("    " * 2 + f"\"log\": ", end='')
        if len(var[key]['log']) == 0:
            print('[],')
        else:
            print('[')
            for record in var[key]['log']:
                print("    " * 3 + str(record).replace('*', '').replace('`', '') + ("" if record == var[key]['log'][-1] else ','))
            print("    " * 2 + '],')
        
        # playing
        print("    " * 2 + f"\"playing\": {var[key]['playing']},")
        
        # queue
        print("    " * 2 + f"\"queue\": ", end='')
        if len(var[key]['queue']) == 0:
            print('[],')
        else:
            print('[')
            tmp = 0
            for record in var[key]['queue']:
                tmp += 1
                print("    " * 3 + f"\"{record}\"" + ('' if tmp == len(var[key]['queue']) else ','))
            print("    " * 2 + ']')
        
        print('    ' * 1 + '}' + ('' if idx == len(var.keys()) else ','))
    print('}')