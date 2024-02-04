import cantools
from cantools.database import conversion
import json
import sys
import time
from utils import get_dbc_files

def cantools_json_to_dbc(input_json: str,outfilename: str,dbs=[]):
    with open(input_json) as file:
        can_json_input = json.load(file)

    new_signal_dict = {}

    for signal in can_json_input["signals"]:

        new_signal = cantools.db.Signal(name=signal["name"],start=signal["start"],length=signal["length"])
        new_signal.byte_order=signal["byte_order"]
        new_signal.is_signed=signal["is_signed"]
        new_signal.initial=signal["initial"]
        new_signal.minimum=(signal["min"])
        new_signal.maximum=signal["max"]
        if "conversion" in signal:
            if "is_float" in signal:
                new_signal.is_float=signal["conversion"]["is_float"]
            if "scale" in signal["conversion"]:
                new_signal.scale = signal["conversion"]["scale"]
            if "offset" in signal["conversion"]:
                new_signal.offset = signal["conversion"]["offset"]
            if "choices" in signal["conversion"]:
                new_signal.choices = signal["conversion"]["choices"]
        new_signal.is_multiplexer=signal["is_multiplexer"]
        new_signal.comment=signal["comment"]
        new_signal.unit=signal["units"]
        new_signal_dict[new_signal.name]=new_signal

    list_of_cantools_msgs = []

    for message in can_json_input["messages"]:
        message_info = can_json_input["messages"][message]
        signals = []

        for signal in message_info["signals"]:
            signals.append(new_signal_dict[signal])

        new_message = cantools.db.Message(frame_id=message_info["id"],
                                        name=message,length=message_info["length"],
                                        signals=signals,
                                        senders=message_info["senders"])
        
        new_message.comment=message_info["comment"]
        new_message.is_extended_frame=message_info["is_extended_frame"]
        new_message.bus_name=message_info["bus_name"]
        list_of_cantools_msgs.append(new_message)
        
    for db in dbs:
        for message in db.messages:
            list_of_cantools_msgs.append(message)
            
    nodes = [cantools.db.Node('vcu',"the vehicle control unit"),
             cantools.db.Node('bms'),
             cantools.db.Node('inverter'),
             cantools.db.Node('dash')]
    
    buses = [cantools.db.Bus('ks8', None, 500000)]
    
    new_db = cantools.db.Database(list_of_cantools_msgs,nodes=nodes,buses=buses)
    

    
    cantools.db.dump_file(new_db,outfilename+'.dbc')
    cantools.db.dump_file(new_db,outfilename+'.sym',database_format='sym')




import subprocess
def json_gen():
    args=sys.argv[1]
    filename="dbc-output/"+args
    db_args = ["Orion","PM_CAN","Megasquirt"]
    db_list = []
    for arg in db_args:
        db = get_dbc_files(arg)
        db_list.append(db)
    cantools_json_to_dbc(input_json="can_descriptor.json",outfilename=filename,dbs=db_list)


if __name__ == "__main__":
    json_gen()
