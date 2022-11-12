"""
Authors
1. Ashvin Shivram Gaonkar (agaonka2)
2. Daksh Mehta (dmehta4)

Date - 13 October 2022
"""

#import necessary libraries

import socket
import threading
import argparse
import time


# Global Variables
SIZE = 1024
FORMAT = "utf-8"
SERVERSTATE = 0
SERVERBUSY = False
NUMBEROFBUYER = 0
BUYER_READY = False
AUCTION_TYPE = None
MIN_PRICE = 0
NUMBER_OF_BIDS = 0
ITEM_NAME = ""
SELLER_CONN = None
SELLER_ADDR = None
ACTIVE_BUYER = 0
BID_AND_CON = {}
BIDS = {}
CONS = {}
IP = ""
PORT = 0

#sends the message specified to the seller and closes the socket
def sendMessageToSellerAndCloseConnection(message):
    global SELLER_CONN
    SELLER_CONN.send(message.encode(FORMAT))
    SELLER_CONN.close()

#sends the specified message to the buyer and closes the socket
def sendMessageToBuyerAndCloseConnection(message, conn): 
    conn.send(message.encode(FORMAT))
    conn.close()

def broadcastResultForType2(maxBid, secondHighestBid):
    flag=0
    for bid in list(BID_AND_CON.values()):
        if(bid == maxBid and flag == 0): # the buyer who has the max bid receives this message. However he has to pay only the second highest bid amount
            flag=1
            result = f'Auction finished! \nYou won this item {ITEM_NAME}! Your payment due is ${secondHighestBid} \nDisconnecting from the Auctioneer server. Auction is over\nSeller IP: {SELLER_ADDR}'
            sendMessageToBuyerAndCloseConnection(result, list(BID_AND_CON.keys())[list(BID_AND_CON.values()).index(bid)]) #BID_AND_CON dictionary is used to find the corresponding conn variable to send the message to the winner.
            del BID_AND_CON[list(BID_AND_CON.keys())[list(BID_AND_CON.values()).index(bid)]]
        else:
            result = f'Auction finished! \nUnfortunately you did not win in the last round. \nDisconnecting from the Auctioneer server. Auction is over'
            sendMessageToBuyerAndCloseConnection(result, list(BID_AND_CON.keys())[list(BID_AND_CON.values()).index(bid)]) #BID_AND_CON dictionary is used to find the corresponding conn variable to send the message to the winner.
            del BID_AND_CON[list(BID_AND_CON.keys())[list(BID_AND_CON.values()).index(bid)]]

def broadcastResultForType1(maxBid,CONS):
    flag=0
    for bid in list(BID_AND_CON.values()):
        if(bid == maxBid and flag ==0): # the buyer who has the max bid receives this message.
            flag=1
            result = f'Auction finished! \nYou won this item {ITEM_NAME}! Your payment due is ${maxBid} \nDisconnecting from the Auctioneer server. Auction is over\nSeller IP: {SELLER_ADDR}'
            sendMessageToBuyerAndCloseConnection(result, list(BID_AND_CON.keys())[list(BID_AND_CON.values()).index(bid)]) #BID_AND_CON dictionary is used to find the corresponding conn variable to send the message to the winner.
            del BID_AND_CON[list(BID_AND_CON.keys())[list(BID_AND_CON.values()).index(bid)]]
        else: # rest of the buyers receive this message
            result = f'Auction finished! \nUnfortunately you did not win in the last round. \nDisconnecting from the Auctioneer server. Auction is over'
            sendMessageToBuyerAndCloseConnection(result, list(BID_AND_CON.keys())[list(BID_AND_CON.values()).index(bid)])
            del BID_AND_CON[list(BID_AND_CON.keys())[list(BID_AND_CON.values()).index(bid)]]



#Reset function to flush all the variables to their initial state and to prepare for another round of bidding once the ongoing round is over.
def reset():
    global SERVERSTATE 
    global SERVERBUSY 
    global NUMBEROFBUYER 
    global BUYER_READY 
    global AUCTION_TYPE 
    global MIN_PRICE 
    global NUMBER_OF_BIDS 
    global ITEM_NAME 
    global SELLER_CONN
    global ACTIVE_BUYER 
    global BID_AND_CON 
    global BIDS 
    global CONS
    global IP
    global PORT

    SERVERSTATE = 0
    SERVERBUSY = False
    NUMBEROFBUYER = 0
    BUYER_READY = False
    AUCTION_TYPE = None
    MIN_PRICE = 0
    NUMBER_OF_BIDS = 0
    ITEM_NAME = ""
    SELLER_CONN=None
    ACTIVE_BUYER = 0
    BID_AND_CON = {}
    BIDS = {}
    CONS = {}
    
    tempClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tempClient.connect((IP, PORT))
    serverWelcomeMessage = tempClient.recv(SIZE).decode(FORMAT)
    tempClient.close()


#Returns maximum key from the dictionary. We have used it to find the maximum bid among all bids
def computeWinnerforAuctionType1(bids):
    global BIDS
    return max(list(BIDS.values()))


#Returns the second highest bid out of all bids present in the dictionary. This has been used to find the price in vickrey auction
def computeWinnerforAuctionType2(bidsDict): 
    global BIDS
    bids = []
    for bid in BIDS.values():
        bids.append(bid)
    bids.sort()
    return bids[-2]

#To extract IP and Port number from the command line
def get_command_line_arguments():
    global IP
    global PORT
    parser = argparse.ArgumentParser('Auctioneer')
    parser.add_argument('hostIP', type=str, help='Host IP Number')
    parser.add_argument('hostPort', type=int, help='Host PORT Number')
    args = parser.parse_args()
    IP = args.hostIP
    PORT = args.hostPort
    return args

#Initializes the server socket and waits for connections at the specified IP address and Port number.
def initializeServerSocket(args):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((args.hostIP, args.hostPort))
    server.listen()
    return server

def handleSeller(conn, addr):
    global BUYER_READY
    global AUCTION_TYPE
    global MIN_PRICE
    global NUMBER_OF_BIDS
    global ITEM_NAME
    global BIDS
    global SELLER_CONN
    global SELLER_ADDR

    SELLER_ADDR = addr
    SELLER_CONN = conn

    BIDS = {} 
    while(True):
        sellerWelcomMessage = "Your role is: [Seller] \nPlease submit auction request:"
        conn.send(sellerWelcomMessage.encode(FORMAT)) #send welcome prompt to seller
      
        bidInfo = conn.recv(SIZE).decode(FORMAT) #receive auction request from seller
        elementsInBid = bidInfo.split()
        if len (elementsInBid) == 4: #Error handling and input validation for the received auction request
            try:
                AUCTION_TYPE, MIN_PRICE, NUMBER_OF_BIDS, ITEM_NAME = elementsInBid
                AUCTION_TYPE = int(AUCTION_TYPE)
                MIN_PRICE = int(MIN_PRICE)
                NUMBER_OF_BIDS = int(NUMBER_OF_BIDS)
                if AUCTION_TYPE not in (1,2) or MIN_PRICE < 0 or NUMBER_OF_BIDS < 1 :
                    raise ValueError
                ITEM_NAME = str(ITEM_NAME)
                print("Auction request received. Now waiting for Buyer.")
            except ValueError:
                msg="Invalid Request Information" #if invalid input send feedback to seller and repeat the input process
                conn.send(msg.encode(FORMAT))
                continue
            break
        else:
            msg="Invalid Request Information"
            conn.send(msg.encode(FORMAT))
            continue
    msg1="Server: Auction start"
    BUYER_READY = True # Now seller's auction request is complete and buyers can be connected to the server
    conn.send(msg1.encode(FORMAT)) #send msg to seller to let it know that auction has started
    
def handleBidding(conn,addr,CONS):
    global ACTIVE_BUYER

    bidStartMessage = "The bidding has started!"
    for conn in CONS:
        conn.send(bidStartMessage.encode(FORMAT)) #Sends bidding started message to all the buyers
    for conn in CONS:
        
        ACTIVE_BUYER += 1 #to keep a track of buyers
        bidAmount = int(conn.recv(SIZE).decode(FORMAT)) #receive bid from the buyer
        BIDS[CONS[conn]] = bidAmount
        BID_AND_CON[conn] = bidAmount #append bid and the conn variable to a dictionary
        print(f'>> Buyer {ACTIVE_BUYER} bid ${bidAmount}') #outputs the buyer number and the respective bid on the server terminal
    
    
    if AUCTION_TYPE == 1: #if it is a first price auction
        maxBid = computeWinnerforAuctionType1(BIDS) #calculate the maximum bid out of all bids
        print(f"Item sold! The highest bid is ${maxBid}.")
        feedbackMessage = f"Success! Your item {ITEM_NAME} has been sold for ${maxBid}"
        sendMessageToSellerAndCloseConnection(feedbackMessage) #updates seller and closes the respective socket
        broadcastResultForType1(maxBid, CONS) # Lets all buyers know whether they won/lost
    elif AUCTION_TYPE == 2: #if it is a vickrey auction
        maxBid = computeWinnerforAuctionType1(BIDS)
        secondHighestBid = computeWinnerforAuctionType2(BIDS)
        print(f"Item sold! The highest bid is ${maxBid}. The actual payment is ${secondHighestBid}") #since it is a vickrey auction highest bidder wins but has to pay the second highest bid
        feedbackMessage = f"Success! Your item {ITEM_NAME} has been sold for ${secondHighestBid}"
        sendMessageToSellerAndCloseConnection(feedbackMessage)
        broadcastResultForType2(maxBid, secondHighestBid)

def handleBuyer(conn, addr):
    try:
        global BIDS
        global MIN_PRICE
        global CONS
        global IP
        global PORT

        CONS[conn]=addr # create a dictionary of connections to keep a track of buyers
        buyerWelcomMessage = "Your role is: [Buyer]"
        conn.send(buyerWelcomMessage.encode(FORMAT)) #send the buyer welcome msg
        conn.send(str(MIN_PRICE).encode(FORMAT)) #send the minimum bidding price to the buyer 
        time.sleep(0.1) # execution pauses for a few miliseconds to synchronize the message exchange
        if NUMBEROFBUYER < NUMBER_OF_BIDS:
            waitingForBuyer = 'The Auctioneer is still waiting for other Buyer to connect...'
            conn.send(waitingForBuyer.encode(FORMAT)) #send a msg to the buyer to let it know that server is waiting for more buyers to join
        elif NUMBEROFBUYER == NUMBER_OF_BIDS:
            time.sleep(0.1)
            print("Requested number of bidders arrived. Let's start bidding") #once the number of buyers is equal to the number of bids specified
            msg3='All Buyers connected...'                                    #by the seller it spawns a new thread to handle the bidding inputs.
            conn.send(msg3.encode(FORMAT))
            biddingThread = threading.Thread(target=handleBidding, args=(conn,addr,CONS)) #spawn thread to handle input bids
            biddingThread.daemon = True
            biddingThread.start()
            print(">> New Bidding Thread spawned")
        biddingThread.join()    # Wait for bidding to get over 
        reset() # Once auction is complete prepare for next round by resetting server state to 0 and flushing all variables
    except:
        pass

def main():

    args = get_command_line_arguments()    #extract IP & Port from command line

    global SERVERSTATE
    global NUMBEROFBUYER
    global BUYER_READY

    server = initializeServerSocket(args) #create server socket and start listening 
    print("Auctioneer is ready for hosting auctions!")

    while True:
        if SERVERSTATE == 0:  #Server state 0 means it is waiting for seller to connect
            conn, addr = server.accept()
            sellerThread = threading.Thread(target=handleSeller, args=(conn, addr)) #Spawn a new thread to handle the seller input
            sellerThread.daemon = True
            print(f"Seller is connected from {addr[0]}:{addr[1]}")
            sellerThread.start() #Starts the seller thread
            print('>> New Seller Thread spawned')
            SERVERSTATE = 1 #Change server state to 1 so that buyers can be connected now
        else: #If someone other than seller is connecting
            conn, addr = server.accept()
            if not BUYER_READY:
                busyResponse = "Server is busy. Try to connect again later." # If buyer is not ready it means seller thread is still busy taking auction request from the seller
                conn.send(busyResponse.encode(FORMAT))
                conn.close()
            else:
                if NUMBEROFBUYER < NUMBER_OF_BIDS: #else accept connections from buyers until total number of bids is reached
                    NUMBEROFBUYER += 1 #increment number of buyers
                    print(f"Buyer {NUMBEROFBUYER} is connected from {addr[0]}:{addr[1]}") #output buyer number and its address 
                    buyerThread = threading.Thread(target=handleBuyer, args=(conn, addr)) #spawn buyer thread which handles the buyers 
                    buyerThread.daemon = True
                    buyerThread.start() # start the buyer thread
                else: #if buyers are equal to number of bids dont accept more connections and let the client know that bidding is in progress
                    busyResponse = "Bidding on-going!"
                    conn.send(busyResponse.encode(FORMAT))
                    conn.close()
        
if __name__ == "__main__":
    main()
