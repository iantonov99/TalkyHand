import socket
import threading

class ChatSender:
    def __init__(self, host, port):
        # self.app = app

        self.host = host
        self.port = port


    def setup_client(self):
        print("SETUP CLIENT")
        self.client_socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket_send.settimeout(5)
        self.client_socket_send.connect((self.host, self.port))

        print("CONNECTED!")

        """
        while True:
            message = input("Enter a message: ")
            self.send_message(message)
        """

    def send_message(self, message):
        print("SENDING:", message)
        self.client_socket_send.send(message.encode())

    def close(self):
        self.client_socket_send.close()


if __name__ == "__main__":
    try:
        host = "192.168.126.52"
        receive_port = 5555
        sender = ChatSender(host, receive_port)
    except Exception as e:
        print("Error:", e)
        exit()

    