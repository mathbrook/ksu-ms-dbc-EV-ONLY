import cantools
from cantools.database import conversion
import json
import sys
import subprocess
from utils import get_dbc_files

def cantools_json_to_dbc(input_json: str,outfilename: str,dbs=[]):
    with open(input_json) as file:
        can_json_input = json.load(file)

    new_signal_dict = {}

    for signal in can_json_input["signals"]:
        print(f"processing signal: {signal['name']}")
        new_signal = cantools.db.Signal(name=signal["name"],start=signal["start"],length=signal["length"])
        try:
            new_signal.byte_order=signal["byte_order"]
        except KeyError as e:
           print(f"\tbyte order not specified for {signal['name']}")
        try:
            new_signal.is_signed=signal["is_signed"]
        except KeyError as e:
           print(f"\tSigned not specified for {signal['name']}")
            
        try:
            new_signal.initial=signal["initial"]
        except:
           print(f"\tno initial value specified for {signal['name']}")
        try:
            new_signal.minimum=(signal["min"])
        except:
           print(f"\tminimum not specified for {signal['name']}")
           new_signal.minimum = 0
        try:
            new_signal.maximum=signal["max"]
        except:
           print(f"\tmax not specified for {signal['name']}")
           # Set max to largest possible value for the length
           new_signal.maximum = 2**(new_signal.length) - 1
        if "conversion" in signal:
            if "is_float" in signal:
                new_signal.is_float=signal["conversion"]["is_float"]
            if "scale" in signal["conversion"]:
                new_signal.scale = signal["conversion"]["scale"]
            if "offset" in signal["conversion"]:
                new_signal.offset = signal["conversion"]["offset"]
            if "choices" in signal["conversion"]:
                new_signal.choices = signal["conversion"]["choices"]
        try:
            new_signal.is_multiplexer=signal["is_multiplexer"]
        except:
           print(f"\tmux not specified for {signal['name']}")
        try:
            new_signal.multiplexer_ids = signal["multiplexer_ids"]
        except:
           print(f"\tmux ids not specified for {signal['name']}")
        try:
            new_signal.multiplexer_signal=signal["multiplexer_signal"]
        except:
           print(f"\tmux signal not specified for {signal['name']}")
        try:
            new_signal.comment=signal["comment"]
        except:
           print(f"\tno comment specified for {signal['name']}")
        try:
            new_signal.unit=signal["units"]
        except:
           print(f"\tno units specified for {signal['name']}")
        new_signal_dict[new_signal.name]=new_signal
        print("")

    list_of_cantools_msgs = []

    for message in can_json_input["messages"]:
        message_info = can_json_input["messages"][message]
        signals = []

        for signal in message_info["signals"]:
            signals.append(new_signal_dict[signal])

        new_message = cantools.db.Message(frame_id=message_info["id"],
                                        name=message,length=message_info["length"],
                                        signals=signals,
                                        senders=(message_info['senders'] if 'senders' in message_info.keys() else None))
        try:
            new_message.comment=message_info["comment"]
        except:
            print(f"No comment found for message {message}")
        new_message.is_extended_frame= (message_info.get("is_extended_frame") if message_info.get("is_extended_frame") is not None else False)
        if new_message.frame_id > 2047:
            new_message.is_extended_frame=True
        try:
            new_message.bus_name=message_info["bus_name"]
        except:
            print(f"No bus specified for message {message}")
        list_of_cantools_msgs.append(new_message)
        
    for db in dbs:
        for message in db.messages:
            list_of_cantools_msgs.append(message)
            
    nodes = [cantools.db.Node('vcu',"the vehicle control unit"),
             cantools.db.Node('bms'),
             cantools.db.Node('inverter'),
             cantools.db.Node('dash')]
    
    buses = [cantools.db.Bus('ks7', "can bus of KSU motorsports vehicles", 500000)]
    
    new_db = cantools.db.Database(list_of_cantools_msgs,nodes=nodes,buses=buses)
    build_version  = subprocess.run(['git','rev-parse','--short', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    build_version.strip()
    new_db.version=build_version
    print(f"Generated DBC hash: {new_db.version}")
    
    cantools.db.dump_file(new_db,outfilename+'.dbc')
    cantools.db.dump_file(new_db,outfilename+'.sym',database_format='sym')




def json_gen(outfile,infile,dbs):

    filename=outfile
    inputfile=infile
    db_args = dbs
    db_list = []
    for arg in db_args:
        db = get_dbc_files(arg)
        db_list.append(db)
    cantools_json_to_dbc(input_json=inputfile,outfilename=filename,dbs=db_list)


if __name__ == "__main__":
    print(sys.argv)
    args_outfile=sys.argv[1]
    args_infile=sys.argv[2]
    args_other_dbcs = sys.argv[3:]
    print(args_other_dbcs)
    json_gen(args_infile,args_outfile,args_other_dbcs)
