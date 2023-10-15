import socket
import threading

class ChatReceiver:
    def __init__(self):
        self.server_host = "0.0.0.0"
        self.server_port = 5555
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(1)  # Maximum 1 connection at a time
        self.client_socket, self.client_address = self.server_socket.accept()

        self.current_message = ""

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
                self.current_message = received_text
                

            except ConnectionResetError:
                print("Connection closed by the other side.")
                break

    # TODO: lock the resource
    def get_message(self):
        message = self.current_message
        self.current_message = ""

        return message

    def close(self):
        self.client_socket.close()
        self.server_socket.close()

if __name__ == "__main__":
    # Create a ChatReceiver object
    receiver = ChatReceiver()