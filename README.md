# Hash Table Benchmarker: Robin Hood vs. Linear Probing

## What is this?
This is a Python-based algorithmic benchmarking tool I built to analyze and compare the performance of different open-addressing hash table implementations. Instead of using Python's native dictionaries, I wrote custom hash tables from scratch to test how standard Linear Probing holds up against the highly optimized Robin Hood Hashing algorithm under extreme load.

## How It All Fits Together
To keep the logic clean and the experiments scientifically fair, I split the architecture into a few core pieces:

* **Entry Class:** A simple data container that stores the key, the value, and tracks the PSL (Probe Sequence Length) for each item.
* **LinearProbingHashTable:** The baseline algorithm. It handles collisions by simply stepping forward to the next available slot. It uses a tombstone-free backward shifting method for deletions to maintain data integrity.
* **RobinHoodHashTable:** The optimized algorithm. It actively manages collisions during insertion by tracking the PSL. 
* **The Benchmarking Suite:** An experimental testing environment that generates thousands of random, clustered, and mixed operations (puts, gets, removes) to stress-test both tables.

## Handling Collisions: The Robin Hood Method
Standard linear probing falls apart when data clumps together, creating massive clusters that destroy lookup times. 

I implemented Robin Hood hashing to fix this. When a collision happens during insertion, the algorithm checks the "wealth" (the Probe Sequence Length) of the new item versus the item currently occupying the slot. If the new item has traveled further from its original hash index (higher PSL), it forcefully swaps places with the existing item, ensuring that the maximum lookup time across the entire table stays strictly balanced.

## The Performance Breakdown
A nice part of this project is the automated evaluation framework. You can run the main script to trigger a head-to-head showdown between both hash tables. 

The system tests both algorithms across three load factors (50%, 80%, and 90% capacity) and three different workload types (Random, Clustered, and Mixed). It outputs a clean terminal table detailing the exact Execution Time, Average PSL, and Operations Per Second (Throughput) for every single test.
