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
    def init_socket(self):
        '''
        Creates a socket,
        binds it to the server addr
        and listens for connections
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(self.server_addr)
        sock.listen(1)
        self.sock = sock
        return sock
    def wait_for_connection(self):
        '''
        Waits for any incoming connection
        When one is received,
        handles it and then closes the connection
        '''
        # self.connection is a new socket object
        # and client_address is the address bound to the socket
        # on the other hand of the connection
        self.connection, client_address = self.sock.accept()
        print(f"Connection from: ", client_address)
        try:
            self.handle_connection()
        finally:
            self.connection.close()
    def start_server(self):
        try:
            self.init_socket()
            while True:
                self.wait_for_connection()
        finally:
            self.sock.close()
