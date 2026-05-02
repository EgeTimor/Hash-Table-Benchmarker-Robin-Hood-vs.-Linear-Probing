import time
import random
import statistics

# PART 1: Robin Hood Hash Table (The Technique)

class Entry:
    def __init__(self, key, value, psl=0):
        self.key = key
        self.value = value
        self.psl = psl

    def __repr__(self):
        return f"[{self.key}:{self.value} (PSL:{self.psl})]"


class RobinHoodHashTable:

    #Implementation of Robin Hood Hashing.

    def __init__(self, capacity=16, load_factor_threshold=0.9):
        self.capacity = capacity
        self.size_count = 0
        self.table = [None] * capacity
        self.load_factor_threshold = load_factor_threshold
        self.total_probes_for_stats = 0  # Metric for evaluation

    def _hash(self, key):
        return hash(key) % self.capacity

    def size(self):
        return self.size_count

    def put(self, key, value):
        # 1: Updates existing key if present
        idx = self._hash(key)
        dist = 0
        while True:
            entry = self.table[idx]
            if entry is None or dist > entry.psl:
                break
            if entry.key == key:
                entry.value = value
                return
            dist += 1
            idx = (idx + 1) % self.capacity

        # 2: Resizes if needed
        if (self.size_count + 1) / self.capacity > self.load_factor_threshold:
            self._resize()

        # 3. Robin Hood Insert
        current_psl = 0
        entry_to_insert = Entry(key, value, current_psl)
        idx = self._hash(key)

        while True:
            self.total_probes_for_stats += 1
            entry_at_idx = self.table[idx]

            if entry_at_idx is None:
                self.table[idx] = entry_to_insert
                self.size_count += 1
                return

            # SWAP condition: Rich (short PSL) takes from the Poor (long PSL)
            if entry_to_insert.psl > entry_at_idx.psl:
                entry_to_insert, self.table[idx] = self.table[idx], entry_to_insert

            entry_to_insert.psl += 1
            idx = (idx + 1) % self.capacity

    def get(self, key):
        idx = self._hash(key)
        current_psl = 0
        while True:
            self.total_probes_for_stats += 1
            entry = self.table[idx]
            if entry is None or current_psl > entry.psl:
                return None
            if entry.key == key:
                return entry.value
            current_psl += 1
            idx = (idx + 1) % self.capacity

    def contains(self, key):
        return self.get(key) is not None

    def remove(self, key):
        # Tombstone-free deletion (Backward Shifting)
        idx = self._hash(key)
        current_psl = 0
        while True:
            self.total_probes_for_stats += 1
            entry = self.table[idx]
            if entry is None or current_psl > entry.psl:
                return False
            if entry.key == key:
                self._backward_shift(idx)
                self.size_count -= 1
                return True
            current_psl += 1
            idx = (idx + 1) % self.capacity

    def _backward_shift(self, empty_idx):
        next_idx = (empty_idx + 1) % self.capacity
        while True:
            entry = self.table[next_idx]
            if entry is None or entry.psl == 0:
                self.table[empty_idx] = None
                return
            entry.psl -= 1
            self.table[empty_idx] = entry
            empty_idx = next_idx
            next_idx = (next_idx + 1) % self.capacity

    def _resize(self):
        old_table = self.table
        self.capacity *= 2
        self.table = [None] * self.capacity
        self.size_count = 0
        for entry in old_table:
            if entry is not None:
                self.put(entry.key, entry.value)

    def get_avg_psl(self):
        total_psl = 0
        count = 0
        for entry in self.table:
            if entry:
                total_psl += entry.psl
                count += 1
        return total_psl / count if count > 0 else 0

# Part 2: Linear Probing Hash Table (The Baseline)
class LinearProbingHashTable:
    def __init__(self, capacity=16, load_factor_threshold=0.9):
        self.capacity = capacity
        self.size_count = 0
        self.table = [None] * capacity
        self.load_factor_threshold = load_factor_threshold
        self.total_probes_for_stats = 0

    def _hash(self, key):
        return hash(key) % self.capacity

    def size(self):
        return self.size_count

    def put(self, key, value):
        # Updating existing
        idx = self._hash(key)
        start_idx = idx
        while True:
            entry = self.table[idx]
            if entry is None: break
            if entry.key == key:
                entry.value = value
                return
            idx = (idx + 1) % self.capacity
            if idx == start_idx: break

        if (self.size_count + 1) / self.capacity > self.load_factor_threshold:
            self._resize()#resize

        # Standard Linear Insertion
        idx = self._hash(key)
        current_psl = 0

        while True:
            self.total_probes_for_stats += 1
            if self.table[idx] is None:
                self.table[idx] = Entry(key, value, current_psl)
                self.size_count += 1
                return

            current_psl += 1
            idx = (idx + 1) % self.capacity

    def get(self, key):
        idx = self._hash(key)
        start_idx = idx
        while True:
            self.total_probes_for_stats += 1
            entry = self.table[idx]
            if entry is None:
                return None
            if entry.key == key:
                return entry.value
            idx = (idx + 1) % self.capacity
            if idx == start_idx: return None

    def contains(self, key):
        return self.get(key) is not None

    def remove(self, key):
        idx = self._hash(key)
        start_idx = idx
        while True:
            self.total_probes_for_stats += 1
            entry = self.table[idx]
            if entry is None: return False
            if entry.key == key:
                self._backward_shift(idx)
                self.size_count -= 1
                return True
            idx = (idx + 1) % self.capacity
            if idx == start_idx: return False

    def _backward_shift(self, empty_idx):
        # Simplified backwards shift to compare the baselines
        next_idx = (empty_idx + 1) % self.capacity
        while True:
            entry = self.table[next_idx]
            if entry is None:
                self.table[empty_idx] = None
                return

            # Re-inserting chain elements to maintain correctness
            temp = entry
            self.table[next_idx] = None
            self.size_count -= 1
            self.table[empty_idx] = temp
            self.size_count += 1

            empty_idx = next_idx
            next_idx = (next_idx + 1) % self.capacity

    def _resize(self):
        old_table = self.table
        self.capacity *= 2
        self.table = [None] * self.capacity
        self.size_count = 0
        for entry in old_table:
            if entry is not None:
                self.put(entry.key, entry.value)

    def get_avg_psl(self):
        total_psl = 0
        count = 0
        for entry in self.table:
            if entry:
                # Recalculating true PSL for LP stats
                home = self._hash(entry.key)
                current_idx = self.table.index(entry)  # finds current index

                dist = (current_idx - home + self.capacity) % self.capacity
                total_psl += dist
                count += 1
        return total_psl / count if count > 0 else 0


# Part 3: Experimental Evaluation

def generate_random_workload(count):
    return [("put", f"key_{random.randint(0, 100000)}", i) for i in range(count)]


def generate_clustered_workload(count):
    # Sequential keys create collisions in modulo arithmetic
    return [("put", f"key_{i}", i) for i in range(count)]


def generate_mixed_workload(count, dataset_size=1000):
    ops = []
    keys = [f"key_{i}" for i in range(dataset_size)]
    for _ in range(count):
        op = random.choice(["put", "get", "get", "remove"])  # 25% put, 50% get, 25% remove
        key = random.choice(keys)
        ops.append((op, key, random.randint(1, 100)))
    return ops


def run_experiment(name, table_cls, load_factor, workload_type, num_ops=10000):
    # Initialize table
    initial_cap = int(num_ops / load_factor)
    # Disable auto-resize for pure load testing by setting threshold > 1.0
    ht = table_cls(capacity=initial_cap, load_factor_threshold=1.1)

    # Generates Workload
    if workload_type == "random":
        workload = generate_random_workload(num_ops)
    elif workload_type == "clustered":
        workload = generate_clustered_workload(num_ops)
    elif workload_type == "mixed":
        # Pre-fills table for mixed operations
        for i in range(int(num_ops * load_factor)):
            ht.put(f"key_{i}", i)
        workload = generate_mixed_workload(num_ops, dataset_size=int(num_ops * load_factor))

    start_time = time.time()

    # Runs Workload
    for op, key, val in workload:
        if op == "put":
            ht.put(key, val)
        elif op == "get":
            ht.get(key)
        elif op == "remove":
            ht.remove(key)

    end_time = time.time()
    duration = end_time - start_time
    throughput = num_ops / duration if duration > 0 else 0
    avg_psl = ht.get_avg_psl()

    return {
        "Technique": name,
        "Load": load_factor,
        "Workload": workload_type,
        "Time(s)": f"{duration:.4f}",
        "Throughput(ops/s)": f"{throughput:.0f}",
        "Avg PSL": f"{avg_psl:.2f}"
    }

#Part 4: Main Execution

if __name__ == "__main__":
    print("--- 1. Running Basic Tests ---")
    rh = RobinHoodHashTable(capacity=8)
    rh.put("test", 1)
    assert rh.get("test") == 1
    assert rh.contains("test") is True
    rh.remove("test")
    assert rh.contains("test") is False
    print("Basic tests have been passed.\n")

    print("--- 2. Starting Experimental Evaluation ---")
    results = []

    # 3 Load Factors
    load_factors = [0.5, 0.8, 0.9]
    # 3 Workloads
    workloads = ["random", "clustered", "mixed"]

    # Comparing Robin Hood vs Linear Probing:
    for load in load_factors:
        for wd in workloads:
            # Runs Robin Hood
            res_rh = run_experiment("RobinHood", RobinHoodHashTable, load, wd)
            results.append(res_rh)

            # Runs Baseline
            res_lp = run_experiment("LinearProbing", LinearProbingHashTable, load, wd)
            results.append(res_lp)

    # The Output Table:
    print(f"{'Technique':<15} | {'Load':<5} | {'Workload':<10} | {'Time(s)':<8} | {'Avg PSL':<8} | {'Ops/Sec':<10}")
    print("-" * 75)
    for r in results:
        print(
            f"{r['Technique']:<15} | {r['Load']:<5} | {r['Workload']:<10} | {r['Time(s)']:<8} | {r['Avg PSL']:<8} | {r['Throughput(ops/s)']:<10}")

    print("\nDone.")