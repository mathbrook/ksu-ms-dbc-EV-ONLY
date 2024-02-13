import can
import cantools



def decode_can_message(msg, db):
    decoded_msg = db.decode_message(msg.arbitration_id, msg.data)
    print(decoded_msg)


def main(dbc_file_path):
    # Load the DBC file
    db = cantools.db.load_file(dbc_file_path)

    # Initialize the CAN interface
    bus = can.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
    # Main loop to receive and decode CAN messages
    while True:
        try:
            # Receive a CAN message with a timeout of 1 second
            msg = bus.recv(timeout=1.0)
            if msg is not None:
                try:
                    decode_can_message(msg, db)
                except:
                    pass
        except KeyboardInterrupt:
            break

    # Cleanup
    bus.shutdown()


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: decode_can.py <dbc_file_path>")
    else:
        dbc_file_path = sys.argv[1]
        main(dbc_file_path)
