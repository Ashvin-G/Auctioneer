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
    args = parser.parse_args()
    return args

def main():
    args = get_command_line_arguments()
    client = createClientSocket(args)
    print('Connected to the Auctioneer server')
    connected = True
    while connected:
        serverWelcomeMessage = client.recv(SIZE).decode(FORMAT)
        print(serverWelcomeMessage) # Server will send welcome prompt and based on that client can connect
        if serverWelcomeMessage == SERVER_BUSY: # This is the stage where Seller have not completed the auction request to Server
            connected = False
            client.close()
        if serverWelcomeMessage == SELLER_ROLE: # This is the first client. i.e. Seller
            bidInfo = input("Enter Bid Information: ")
            client.send(bidInfo.encode(FORMAT)) # Sends the auction request to Server
            reply=client.recv(SIZE).decode(FORMAT) # Wait for feedback from Server i.e. data validation feedback
            print(reply)
            if reply == INVALID_REQUEST: # If invalid auction request. Continue unitl Seller sends valid requests
                continue
            else:
                reply2=client.recv(SIZE).decode(FORMAT) # Waiting for Server Auction Start Prompt.
                print(reply2)
                reply3=client.recv(SIZE).decode(FORMAT) # Waiting for Auction results.
                print(reply3)
                connected=False
                client.close()
        if serverWelcomeMessage == BUYER_ROLE: # Client connect as buyer
            minBidAmount = int(client.recv(SIZE).decode(FORMAT)) # Buyer receives minimum price for item from server
            rep=client.recv(SIZE).decode(FORMAT) # Waiting for "waiting for other buyer" prompt
            print(rep)
            rep2=client.recv(SIZE).decode(FORMAT) # Waiting for bidding start prompt
            print(rep2)
            print('')
            while(True): # Bid Validation of Buyer
                try:
                    bidAmount=int(input('Please submit your bid: '))
                except:
                    print(f"Invalid Bidding Amount. Amount should be a positive integer greater than {minBidAmount}")
                    continue
                else:
                    while bidAmount < minBidAmount:
                        try:
                            print(f"Invalid Bidding Amount. Amount should be a positive integer greater than {minBidAmount}")   
                            bidAmount = int(input("Enter Bid Amount: "))
                        except:
                            continue
                    break                          
            client.send(str(bidAmount).encode(FORMAT)) # Send bid to Server
            print('Bid received. Please wait...')
            txt=client.recv(SIZE).decode(FORMAT) # Buyer waiting for auction results.
            print(txt)
            connected=False # Once the result is published connection is closed.
            client.close()         

        if serverWelcomeMessage == BID_ONGOING: # Handles if another Buyer tries to connect in middle of the on-going bidding.
            connected = False
            client.close()

if __name__ == "__main__":
    main()
