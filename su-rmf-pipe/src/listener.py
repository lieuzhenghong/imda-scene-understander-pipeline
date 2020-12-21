from io import BytesIO
import socket

class Listener:
    from typing import Tuple
    HEADER_SIZE = 10
    def __init__(self, server_addr: Tuple[str, int], 
                handle_data_fn
                ):
        self.server_addr = server_addr
        self.handle_data_fn = handle_data_fn
    @staticmethod
    def recv_all(msg_len, connection):
        '''
        Receives data of msg_len in chunks of 4096 bits
        and returns a BytesIO filled with that data
        '''
        full_data = BytesIO()
        while (full_data.getbuffer().nbytes < msg_len):
            data = connection.recv(4096)
            full_data.write(data)
        full_data.seek(0)
        return full_data
    def decode_message(self, connection) -> BytesIO:
        b_msg_len = connection.recv(Listener.HEADER_SIZE)
        msg_len = int(b_msg_len.decode("utf-8"))
        print(msg_len)
        # receive the data in small chunks
        full_data = Listener.recv_all(msg_len, connection)
        print("All data received!")
        return full_data
    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.server_addr)
            sock.listen(1)
            try:
                while True:
                    print('waiting for a connection')
                    connection, client_address = sock.accept()
                    try:
                        print(f"Connection from: ", client_address)

                        b_full_data = self.decode_message(connection)
                        b_return_data = self.handle_data_fn(b_full_data)

                        connection.sendall(b_return_data.read())

                    # Use a try:finally block to close even in the event of an error
                    finally:
                        connection.close()
            finally:
                print("Closing socket..")
            sock.close()
