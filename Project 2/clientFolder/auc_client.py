"""
Authors
1. Ashvin Shivram Gaonkar (agaonka2)
2. Daksh Mehta (dmehta4)

Date - 13 October 2022
"""

# Import required libraries
import socket
import argparse
import time
import numpy as np

rate = 0.8

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


def extract_type(msg):
    return int(msg.split(';{{}};')[1])


def extract_seq(msg):
    return int(msg.split(';{{}};')[2])


def extract_data(msg):
    return msg.split(';{{}};')[0]


def rectify(a):
    if a == 1:
        return 0
    else:
        return 1


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
            client.send((str(bidAmount)+";"+str(args.rdtPort)
                         ).encode(FORMAT))  # Send bid to Server
            print('Bid received. Please wait...')
            # Buyer waiting for auction results.
            txt = client.recv(SIZE).decode(FORMAT)
            print(txt)
            ##################################################################
            txt = txt.split()
            if txt[3] == "won":
                clientPart2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                clientPart2.bind(("127.0.0.1", args.rdtPort))
                print("UDP Socket opened for RDT")
                print('Start receiving file')
                file_name = "testing.docx"
                # print('file name is ', file_name)
                seq = 0
                flag = 0
                data = []
                while True:
                    if (flag == 0):
                        flag = 1
                        msg, connPart2 = clientPart2.recvfrom(10000)
                        if ((np.random.binomial(n=1, p=rate)) == 1):
                            msg = msg.decode('utf-8')
                            file_size = int(msg.split(';{{}};')[0].split()[1])
                            msg_type = extract_type(msg)
                            recv_seq = extract_seq(msg)
                            if (recv_seq == seq):
                                print('Sequence Received:', recv_seq)
                                seq = 1 if seq == 0 else 0
                                ack = str(seq)
                                print('ACk sent:', rectify(int(ack)))
                                clientPart2.sendto(
                                    ack.encode('utf-8'), connPart2)
                                print(extract_data(msg))
                            else:
                                print('Msg received with mismatched sequence number',
                                      recv_seq, '. Expecting ', rectify(recv_seq))
                        else:
                            print('PACKET DROPPED:', seq)
                            print()
                    else:
                        msg, connPart2 = clientPart2.recvfrom(10000)
                        if ((np.random.binomial(n=1, p=rate)) == 1):
                            msg = msg.decode('utf-8')
                            msg_type = extract_type(msg)
                            recv_seq = extract_seq(msg)
                            if (recv_seq == seq):
                                if (extract_data(msg) == 'fin'):
                                    print('Msg received:', recv_seq)
                                    seq = 1 if seq == 0 else 0
                                    ack = str(seq)
                                    print('ACk sent:', rectify(int(ack)))
                                    print()
                                    clientPart2.sendto(
                                        ack.encode('utf-8'), connPart2)
                                    # print('encountered fin')
                                    print('All Data Received! Exiting...')
                                    break
                                else:
                                    data.append(extract_data(msg))
                                    print('Msg received:', recv_seq)
                                    # print('Received data seq', recv_seq)
                                    # print(data)
                                    seq = 1 if seq == 0 else 0
                                    ack = str(seq)
                                    print('ACk sent: ', rectify(int(ack)))
                                    print()
                                    clientPart2.sendto(
                                        ack.encode('utf-8'), connPart2)
                            else:
                                print(extract_data(msg))
                                clientPart2.sendto(
                                    recv_seq.encode('utf-8'), connPart2)
                                print('Out of order packet')
                        else:
                            print('PACKET DROPPED:', seq)
                            print()
                print(data)
                # print('type of message is ', msg_type, ' sequence number - ', seq)
                # print('file size recvd: ', file_size)
                # print(type(data[0]))

                # with open("temp.txt", "wb") as file:
                #     for d in data:
                #         file.write(d[2:-1].encode(FORMAT))

                # while True:
                #     msg, conn = clientPart2.recvfrom(10000)
                #     print(msg)

            ###################################################################
            # Once the result is published connection is closed.
            else:
                connected = False
                client.close()

        # Handles if another Buyer tries to connect in middle of the on-going bidding.
        if serverWelcomeMessage == BID_ONGOING:
            connected = False
            client.close()


if __name__ == "__main__":
    main()
