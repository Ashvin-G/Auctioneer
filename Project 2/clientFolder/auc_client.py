"""
Authors
1. Ashvin Shivram Gaonkar (agaonka2)
2. Daksh Mehta (dmehta4)

Date - 13 October 2022
"""

# Import required libraries
import socket
import argparse

# Define global variables
SIZE = 1024
FORMAT = "utf-8"
SERVER_BUSY = "Server is busy. Try to connect again later."
SELLER_ROLE = "Your role is: [Seller] \nPlease submit auction request:"
BUYER_ROLE = "Your role is: [Buyer]"
INVALID_REQUEST = "Invalid Request Information"
BID_ONGOING = "Bidding on-going!"

# Create client socket and connect to server Port Number


def createClientSocket(args):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((args.clientIP, args.hostPort))
    return client

# Get the arguments from command line


def get_command_line_arguments():
    parser = argparse.ArgumentParser('Auctioneer')
    parser.add_argument('clientIP', type=str, help='Host IP Number')
    parser.add_argument('hostPort', type=int, help='Host PORT Number')
    parser.add_argument('rdtPort', type=int, help='rdt PORT Number')
    args = parser.parse_args()
    return args


def main():
    args = get_command_line_arguments()
    client = createClientSocket(args)
    print('Connected to the Auctioneer server')
    connected = True
    while connected:
        serverWelcomeMessage = client.recv(SIZE).decode(FORMAT)
        # Server will send welcome prompt and based on that client can connect
        print(serverWelcomeMessage)
        # This is the stage where Seller have not completed the auction request to Server
        if serverWelcomeMessage == SERVER_BUSY:
            connected = False
            client.close()
        if serverWelcomeMessage == SELLER_ROLE:  # This is the first client. i.e. Seller
            bidInfo = input("Enter Bid Information: ")
            # Sends the auction request to Server
            client.send(bidInfo.encode(FORMAT))
            # Wait for feedback from Server i.e. data validation feedback
            reply = client.recv(SIZE).decode(FORMAT)
            print(reply)
            if reply == INVALID_REQUEST:  # If invalid auction request. Continue unitl Seller sends valid requests
                continue
            else:
                # Waiting for Server Auction Start Prompt.
                reply2 = client.recv(SIZE).decode(FORMAT)
                print(reply2)
                # Waiting for Auction results.
                reply3 = client.recv(SIZE).decode(FORMAT)
                print(reply3)
                connected = False
                client.close()
        if serverWelcomeMessage == BUYER_ROLE:  # Client connect as buyer
            # Buyer receives minimum price for item from server
            minBidAmount = int(client.recv(SIZE).decode(FORMAT))
            # Waiting for "waiting for other buyer" prompt
            rep = client.recv(SIZE).decode(FORMAT)
            print(rep)
            # Waiting for bidding start prompt
            rep2 = client.recv(SIZE).decode(FORMAT)
            print(rep2)
            print('')
            while (True):  # Bid Validation of Buyer
                try:
                    bidAmount = int(input('Please submit your bid: '))
                except:
                    print(
                        f"Invalid Bidding Amount. Amount should be a positive integer greater than {minBidAmount}")
                    continue
                else:
                    while bidAmount < minBidAmount:
                        try:
                            print(
                                f"Invalid Bidding Amount. Amount should be a positive integer greater than {minBidAmount}")
                            bidAmount = int(input("Enter Bid Amount: "))
                        except:
                            continue
                    break
            client.send((str(bidAmount)+";"+str(args.rdtPort)).encode(FORMAT))  # Send bid to Server
            print('Bid received. Please wait...')
            # Buyer waiting for auction results.
            txt = client.recv(SIZE).decode(FORMAT)
            print(txt)
            # Once the result is published connection is closed.
            connected = False
            client.close()

        # Handles if another Buyer tries to connect in middle of the on-going bidding.
        if serverWelcomeMessage == BID_ONGOING:
            connected = False
            client.close()


if __name__ == "__main__":
    main()
