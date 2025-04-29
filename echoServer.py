import socket

DB_CONFIG = {
    'host': 'ep-frosty-sea-a6uqgpgz-pooler.us-west-2.aws.neon.tech',
    'port': 5432,
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_zbx9eflUnsh5',
    'sslmode': 'require'
}
TABLE = '"Data_virtual"'

def main():
    # Specify the IP address and port to listen on
    server_ip = input("Enter server IP address: ")
    server_port = int(input("Enter server port number: "))

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind the socket to the IP address and port
        server_socket.bind((server_ip, server_port))

        # Listen for incoming connections
        server_socket.listen(1)
        print("Server is listening on", server_ip, "port", server_port)

        while True:
            # Accept incoming connection
            client_socket, client_address = server_socket.accept()
            print("Connected to client:", client_address)

            while True:
                # Receive message from client
                message = client_socket.recv(1024).decode()
                if not message:
                    break

                print("Received message from client:", message)

                # Change message to uppercase
                response = message.upper()

                print("Message being sent to client:", response)

                # Send response back to client
                client_socket.send(response.encode())

            # Close client socket
            client_socket.close()

    except Exception as e:
        print("An error occurred:", e)
    finally:
        # Close the server socket
        server_socket.close()


if __name__ == "__main__":
    main()
