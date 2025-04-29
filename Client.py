import socket

def clientRun():
    valid_queries = [
        "What is the average moisture inside my kitchen fridge in the past three hours?",
        "What is the average water consumption per cycle in my smart dishwasher?",
        "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
    ]

    # 1. Prompt user for server details
    serverIP = input("Enter Server IP Address: ")
    serverPort = input("Enter Server Port Number: ")

    try:
        serverPort = int(serverPort)  # Convert port to integer
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
    except ValueError:
        print("Error: Port number must be an integer.")
        return
    except (socket.gaierror, socket.error):
        print("Error: Invalid IP address or could not connect to the server.")
        return

    print("Successful Connection!")

    # 3. & 5. Display server reply.
    while True:
        print("\nYou can ask one of the following queries:")
        for query in valid_queries:
            print(f"- {query}")

        myMessage = input("\nEnter your query (or type 'exit' to quit): ")
        if myMessage.lower() == "exit":
            break

        if myMessage not in valid_queries:
            print("\nSorry, this query cannot be processed.")
            print("Please try one of the following:")
            for query in valid_queries:
                print(f"- {query}")
            continue  # Ask again

        # If valid, send to server
        clientSocket.sendall(myMessage.encode("utf-8"))
        response = clientSocket.recv(1024).decode("utf-8")
        print(f"\n Server Response: {response}")

    clientSocket.close()

if __name__ == "__main__":
    clientRun()



