# Auctioneer

## Project Description
This project expands upon the previous auction server and client implementations to facilitate the secure transfer of digital files from the seller to the winning bidder. The primary goal is to ensure reliable delivery of large private files, such as high-resolution images or videos, sold in the auction. The winning bidder should be able to receive the file with utmost reliability. To achieve this, a UDP-based, application-layer reliable data transfer (RDT) protocol is implemented, bypassing the use of TCP due to potential security concerns like SYN attacks.

## Scenario
The project builds on the existing auc_server and auc_client programs and incorporates the UDP-based RDT protocol. After the auction concludes, the auction server acts as an index server in a peer-to-peer transfer scenario. The seller directly transfers the digital file to the winning bidder, assisted by the auction server and other relevant parties. The protocol ensures secure and efficient file transmission, guaranteeing that the winning bidder successfully receives the purchased file.
