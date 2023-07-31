# Auctioneer

## Project Description
This project expands upon the previous auction server and client implementations to facilitate the secure transfer of digital files from the seller to the winning bidder. The primary goal is to ensure reliable delivery of large private files, such as high-resolution images or videos, sold in the auction. The winning bidder should be able to receive the file with utmost reliability. To achieve this, a UDP-based, application-layer reliable data transfer (RDT) protocol is implemented, bypassing the use of TCP due to potential security concerns like SYN attacks.

## Scenario
The project builds on the existing auc_server and auc_client programs and incorporates the UDP-based RDT protocol. After the auction concludes, the auction server acts as an index server in a peer-to-peer transfer scenario. The seller directly transfers the digital file to the winning bidder, assisted by the auction server and other relevant parties. The protocol ensures secure and efficient file transmission, guaranteeing that the winning bidder successfully receives the purchased file.

# Auctioneer Server

## Overview
The Auctioneer Server is an application that facilitates auctions for digital files. It operates in two states: "Waiting for Seller" and "Waiting for Buyer." The server accepts clients over a welcoming TCP port and guides them through the auction process.

## Auction Process
1. When a new client connects, if the server is in "Waiting for Seller" status, the first connected client assumes the Seller role and submits an auction request. Other incoming connections are rejected until the auction request is received.
2. The server decodes the auction request and validates the information provided by the Seller.
3. Once the auction request is successfully received, the server changes to "Waiting for Buyer" status and starts accepting up to a specified number of Buyers for bidding.
4. When the required number of Buyers connects, the bidding process begins. The server handles the bids from Buyers and informs them accordingly.
5. After all bids are received, the server identifies the winning Buyer with the highest bid.
6. If the highest bid meets the minimum price, the auction succeeds, and the server informs the Seller and winning Buyer accordingly, providing their IP addresses.
7. If the highest bid is below the minimum price, the auction fails, and the server notifies the Seller and other clients of the outcome.
8. After the auction concludes, the server resets to "Waiting for Seller" status to handle future auction requests.

Note: This project implements an application-layer reliable data transfer (RDT) protocol for secure file transmission.

# Seller/Buyer Client

## Overview
The Seller and Buyer Clients are applications that participate in the auction process facilitated by the Auctioneer Server. The Seller Client assumes the role of a seller, while the Buyer Client assumes the role of a potential buyer. Both clients implement a unidirectional, Stop-and-Wait reliable data transfer protocol for UDP-based message exchange and file transfer.

## Seller Mode
1. The Seller Client sends an auction request to the Auctioneer Server, specifying auction details.
2. If the auction request is invalid, the client must resend a valid request.
3. Once the auction starts, the Seller Client opens a UDP socket and begins transmitting the file content to the Winning Buyer (WB).
4. The Seller divides the file into chunks of 2000 bytes, each with a maximum segment size.
5. The Seller uses the Stop-and-Wait protocol to send the chunks to WB, handling acknowledgments and retransmissions.
6. After successful transmission, the Seller informs WB of the end-of-transmission and exits.

## Buyer Mode
1. The Buyer Client bids during the auction by sending a positive integer bid to the Auctioneer Server.
2. If the bid is invalid, the client must resend a valid bid.
3. Once the auction result is successful for the Buyer (WB), it opens a UDP socket and listens for messages from the Seller.
4. The Buyer uses the Stop-and-Wait protocol to receive file data and control messages from the Seller.
5. The Buyer ensures proper handling of out-of-order and duplicate messages during transmission.
6. After successful reception of the file, WB saves the content as "recved.file" and exits.

## Packet Loss Model
The simulated network introduces packet loss by discarding UDP messages with a probability determined by the <packet_loss_rate> parameter. This is achieved by generating a random flag using the "numpy.random.binomial" function. The <packet_loss_rate> value ranges between [0.0, 1.0].

## Performance Measurement
The project measures Transfer Completion Time (TCT) and Average Throughput (AT) of the implemented Stop-and-Wait protocol under different network conditions (packet_loss_rates). TCT is the time from sending the full payment until receiving the end-of-transmission message, while AT is the total received data bytes divided by TCT. Multiple runs of the auction with varying <packet_loss_rate> settings are performed, and the observed performance metrics are plotted against the parameter to draw conclusions about the protocol's performance in lossy networks.
