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
        self.connection = None
    def recv_all(self, msg_len):
        '''
        Receives data of msg_len in chunks of 4096 bits
        and returns a BytesIO filled with that data
        '''
        full_data = BytesIO()
        while (full_data.getbuffer().nbytes < msg_len):
            data = self.connection.recv(4096)
            full_data.write(data)
        full_data.seek(0)
        return full_data
    def recv_header(self) -> int:
        '''
        Given an active connection,
        reads the first HEADER_SIZE bytes
        and returns the length of the rest of the payload
        '''
        b_msg_len = self.connection.recv(Listener.HEADER_SIZE)
        msg_len = int(b_msg_len.decode("utf-8"))
        print(msg_len)
        return msg_len
    def handle_connection(self):
        '''
        Once a connection is received,
        we receive the full data in bytes,
        perform some function on that data,
        and return some response to the client.
        '''
        msg_len = self.recv_header()
        # receive the data in small chunks
        b_full_data = self.recv_all(msg_len)
        print("All data received!")
        b_return_data = self.handle_data_fn(b_full_data)
        self.connection.sendall(b_return_data.read())
    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.server_addr)
            sock.listen(1)
            try:
                while True:
                    print('waiting for a connection')
                    self.connection, client_address = sock.accept()
                    print(f"Connection from: ", client_address)
                    try:
                        self.handle_connection()
                    finally:
                        self.connection.close()
            finally:
                print("Closing socket..")
            sock.close()
