import socket
import threading

class ChatSender:
    def __init__(self, host, port):
        # self.app = app

        # setup client as thread
        thread = threading.Thread(target=self.setup_client, args=(host, port))
        thread.daemon = True
        thread.start()


    def setup_client(self, host, port):
        print("SETUP CLIENT")
        self.client_socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket_send.connect((host, port))

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

    