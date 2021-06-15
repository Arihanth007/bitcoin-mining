
from typing import ItemsView


class MempoolTransaction():

    def __init__(self) -> None:
        # pre-defined variables
        self.read_file = 'mempool.csv'
        self.save_file = 'block.txt'
        self.max_weight = 4000000
        # initialised variables
        self.transactions = {}  # all entries from input csv
        self.ratios_dict = {}  # ratios associated with every transaction
        self.isVis = {}  # checking for duplicates
        self.block = []  # contains all transaction in the block
        self.block_weight = 0
        self.block_fee = 0
        self.data_weight = 0
        self.data_fee = 0

    # read from input csv file
    def extract_data(self):
        raw_data = []
        with open(self.read_file) as f:
            for line in f.readlines():
                line = line.strip().split(',')
                try:
                    txid = line[0]
                    fee = int(line[1])
                    weight = int(line[2])
                    parent_txid = []
                    if line[3] != '':
                        parent_txid = line[3].split(';')
                    raw_data.append([txid, fee, weight, parent_txid])
                except:
                    pass

        # format - {txid: {ratio, fee, weight, [parent_txids]}}
        self.transactions = {txid: {'ratio': None, 'fee': fee, 'weight': weight, 'parent_txid': parent_txid} for txid,
                             fee, weight, parent_txid in raw_data}

    # recursively calculates ratios
    # by going through all the parents
    # and taking the mean of all ratios
    def current_ratio(self, txid):

        # if it has no parents
        if self.transactions[txid]['parent_txid'] == []:
            return float(self.transactions[txid]['fee']/self.transactions[txid]['weight'])

        # it has parents and we need to sum all the ratios
        # ratio = fee/weight
        total = float(self.transactions[txid]
                      ['fee']/self.transactions[txid]['weight'])

        # maintain a queue of all parents whose ratio we need
        queue = [i for i in self.transactions[txid]['parent_txid']]
        while len(queue):
            cur_id = queue[0]
            if self.transactions[cur_id]['ratio'] == None:
                # if the parent ratio isn't calculated then
                # recursively check if that has any parents
                # and calculate their ratios before coming back here
                self.transactions[cur_id]['ratio'] = self.current_ratio(cur_id)
            total += self.transactions[cur_id]['ratio']
            queue.remove(cur_id)

        # return the mean ratio of the transaction and its parents
        return float(total/(len(self.transactions[txid]['parent_txid'])+1))

    # calculate the ratio of every transaction
    def calculate_ratios(self):
        for txid, entry in self.transactions.items():
            if self.transactions[txid]['ratio'] == None:
                self.transactions[txid]['ratio'] = self.current_ratio(txid)

    # Making sure parent transactions come before the transaction
    # Calculates the total weight and fee of including a transaction and its parents
    def check_transaction(self, txid):
        # transaction is already present in the block
        if self.isVis[txid]:
            return 0, 0, []

        weight = self.transactions[txid]['weight']
        fee = self.transactions[txid]['fee']
        final_list = [txid]

        self.isVis[txid] = True
        if self.transactions[txid]['parent_txid'] == []:
            return weight, fee, final_list

        # transaction has parents
        queue = [i for i in self.transactions[txid]['parent_txid']]
        # calculate fee and weight contributions
        # traveral will be in incremental levels
        # implementation is similar to that of bfs
        while len(queue):
            parents_to_add = []

            # queue implentation using lists
            # logic - reverse list, append to list, reverse list again
            final_list.reverse()

            for ele in queue:
                if self.isVis[ele]:
                    continue

                self.isVis[ele] = True
                final_list.append(ele)
                weight += self.transactions[ele]['weight']
                fee += self.transactions[ele]['fee']
                for new_id in self.transactions[ele]['parent_txid']:
                    if not self.isVis[new_id]:
                        parents_to_add.append(new_id)

            final_list.reverse()

            queue.clear()
            queue.extend(parents_to_add)

        return weight, fee, final_list

    # Finding the transactions that yeild the highest fee
    def find_best_transaction(self):
        # creating a copy that contains only txid and ratio
        # sorting from highest to lowest values of ratios
        self.ratios_dict = {txid: entry['ratio'] for txid,
                            entry in self.transactions.items()}
        self.ratios_dict = {k: v for k, v in sorted(
            self.ratios_dict.items(), key=lambda item: item[1], reverse=True)}

        # initializing all txid to not visited
        for txid, entry in self.transactions.items():
            self.isVis[txid] = False
            for parent in entry['parent_txid']:
                self.isVis[parent] = False

        # skip if transaction is already in block
        for txid, ratio in self.ratios_dict.items():
            if self.isVis[txid]:
                continue

            temp_weight, temp_fee, temp_trans = self.check_transaction(txid)

            if self.block_weight + temp_weight >= self.max_weight:
                continue

            self.block_weight += temp_weight
            self.block_fee += temp_fee
            self.block.extend(temp_trans)

    # writes the block to a file
    def write_data_to_file(self):
        write_file = open(self.save_file, 'w')
        for line in self.block:
            write_file.write(line+'\n')
        write_file.close()

    # prints some statistics comparing all transactions to transactions in the block
    def print_statistics(self):
        for txid, entry in self.transactions.items():
            self.data_weight += entry['weight']
            self.data_fee += entry['fee']

        print(
            f"Total data weight = {self.data_weight}, total data fee = {self.data_fee}, No.of transactions in data = {len(self.transactions)}")
        print(
            f"Total block weight = {int(self.block_weight)}, Total block fee = {self.block_fee}, No.of transactions in the block = {len(self.block)}")
        print(
            f"Percentage of unused weight = {((4000000-int(self.block_weight))/4000000)*100 :.4}%, percentage of fee collected = {(self.block_fee/self.data_fee)*100 :.2f}%, percentage of transactions = {(len(self.block)/len(self.transactions))*100 :.2f}%")

    # verifying results and cross-checking some values
    # all duplicates must be 0
    def testing(self):
        check_for_duplicates = {txid: int(0) for txid in self.block}
        transaction_duplicates = {txid: int(0)
                                  for txid in self.transactions.keys()}
        print(
            f"\nTransaction duplicates in given data = {len(self.transactions)-len(transaction_duplicates)}")
        print(
            f"Transaction duplicates in our block = {len(self.block)-len(check_for_duplicates)}")


def main():
    transaction = MempoolTransaction()
    transaction.extract_data()
    transaction.calculate_ratios()
    transaction.find_best_transaction()
    transaction.write_data_to_file()
    transaction.print_statistics()
    transaction.testing()


if __name__ == "__main__":
    main()
