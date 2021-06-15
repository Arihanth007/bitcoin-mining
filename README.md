# Bitcoin Mining

## Objective

Maximise the fee collected by the bitcoin miner while minimizing the weight required to do so (contraint being that total weight can exceed a set threshold).

The output must be a block containing transactions that are made such that all parent transaction must appear before the transaction itself.

## Working of the code

The code follows a greedy approach. We first assign a scoring metric to every transaction. The score is equal to the fee divided by the weight. We then sort the transaction in descending order and pick the ones with the highest ratio. When parent transactions are encountered, we include all of them before including the transaction itself.

## Merits of the code

The code runs in O(n) where n is the number of transactions. Thus the code executes very quickly.

## Shortcomings of the code

Since we are considering ratios as the metric that defines which one to pick and not the values themselves we might observe that when the value of weights are comparable to that of the threshold, there is a chance that the generated block isn't the best choice.

## Why this algorithm?

Inspite of the shortcoming, the differnce between the best choice and the output of this code wouldn't be very significant. The naive method would be to consider every subset whose total weight is within the threshold. But this would be a O(2^n) operation where n is the number of transactions.

## Running the code

`python3 main.py`
