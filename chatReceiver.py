import socket
import threading


class ChatReceiver:
    def __init__(self, host, port):
        self.server_host = host
        self.server_port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(1)  # Maximum 1 connection at a time
        self.client_socket, self.client_address = self.server_socket.accept()

        # Start a separate thread for receiving messages
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def receive_messages(self):
        print("LISTENING:")
        while True: 
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                received_text = data.decode()
                print("Received:", received_text)

            except ConnectionResetError:
                print("Connection closed by the other side.")
                break

    def close(self):
        self.client_socket.close()
        self.server_socket.close()

if __name__ == "__main__":
    # Create a ChatReceiver object
    receiver = ChatReceiver('0.0.0.0', 5555)