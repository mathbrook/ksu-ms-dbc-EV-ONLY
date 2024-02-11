import cantools
from cantools.database import conversion
import json
import sys
from utils import get_dbc_files

def cantools_dbc_to_json(db: cantools.db.Database,outfilename: str):

    signals_list = []
    messages_list = {"messages":{}}
    for message in db.messages:
        message_dict= {
            "id": "",
            "length": "",
            "signals":[],
            "comment":"",
            "is_extended_frame":"",
            "bus_name":""
        }
        message_dict["id"] = message.frame_id
        message_dict["length"]=message.length
        # if message.is_multiplexed():
        #     message_dict["signals"]=message.signal_tree
        for signal in message.signals:

            signal_dict = {}
            message_dict["signals"].append(signal.name)
            signal_dict["name"]=signal.name
            signal_dict["start"]=signal.start
            signal_dict["length"]=signal.length
            signal_dict["byte_order"]=signal.byte_order
            signal_dict["is_signed"]=signal.is_signed
            signal_dict["initial"]=signal.initial
            signal_dict["comment"]=signal.comment
            signal_dict["units"]=signal.unit
            signal_conv_type = (type(signal.conversion))

            if signal_conv_type == conversion.IdentityConversion:
                signal_dict["conversion"]={"is_float":"false"}
            elif signal_conv_type == conversion.LinearConversion:
                signal_dict["conversion"]={"scale":signal.scale,"offset":signal.offset,"is_float":signal.is_float}
            elif signal_conv_type == conversion.NamedSignalConversion:
                signal_dict["conversion"]={"scale":signal.scale,"offset":signal.offset,"choices":{}}

                for i in signal.choices:
                    signal_dict["conversion"]["choices"][str(i)]=str(signal.choices[i])

            signal_dict["min"]=signal.minimum
            signal_dict["max"]=signal.maximum
            signal_dict["is_multiplexer"]=signal.is_multiplexer
            signal_dict["multiplexer_ids"]=signal.multiplexer_ids
            signal_dict["multiplexer_signal"]=signal.multiplexer_signal
            signals_list.append(signal_dict)
        message_dict["comment"]=message.comment
        message_dict["bus_name"]=message.bus_name
        message_dict["is_extended_frame"]=message.is_extended_frame
        message_dict["senders"]=message.senders
        messages_list["messages"][message.name]=message_dict
        messages_list["signals"]=signals_list
    
    with open(outfilename+".json","w") as outfile:
        json.dump(messages_list,outfile,indent=4)
        
# Pass in paths to DBC files to turn into json
# Leave spaces between each path
# ie. "python ./dbc_to_json.py ./dbc-files/Orion_CANBUS.dbc ./dbc-files/20200701_RMS_PM_CAN_DBC.dbc"
if __name__ == "__main__":
    args=sys.argv[1:]
    db_args = args
    for arg in db_args:
        db = cantools.db.load_file(arg,'dbc')
        outfilename = input(f"enter outfile name for {arg}: ")
        cantools_dbc_to_json(db,"json-output\\"+outfilename)