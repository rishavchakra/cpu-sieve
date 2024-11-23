from os import path, walk
from datetime import datetime
import numpy as np

"""
Directory structure:

out/miss-ratio/
    1/ (associativity)
    2/
    4/
    ...
        zipf/
        zipf-control/
        seq/
        ...
            fifo/
            lru/
            sieve/
            ...
                1/ (trial)
                2/
                3/
                ...
                    stats.txt
                    ... (not important)
"""

timestr = datetime.now().strftime("out/gem5-%Y-%m-%d-%H-%M-%S.csv")
print("Saving results to:", timestr)
out_file = open(timestr, "a")

out_file.write(
    "Associativity,Algorithm,Access Pattern,Trial Num,Accesses,Hits,Misses,Miss Rate\n"
)

important_stats = [
    "system.cpu.dcache.overallHits::total",
    "system.cpu.dcache.overallMisses::total",
    "system.cpu.dcache.overallAccesses::total",
    # "system.l2cache.overallHits::total",
    # "system.l2cache.overallMisses::total",
    # "system.l2cache.overallAccesses::total",
    # Does not make sense to compare this between accessing vs. control
    # Calculate miss rate based on hit and miss numbers
    # "system.cpu.dcache.overallMissRate::total",
]


class Trial:
    def __init__(
        self, assoc: str, pattern: str, algo: str, trial_num: int, stats: dict
    ):
        self.assoc = assoc
        self.mem_pattern = pattern
        self.algo = algo
        self.trial_num = trial_num
        self.stats = stats


class TrialAverage:
    def __init__(
        self,
        pattern: str,
        algo: str,
        val_hits,
        var_hits,
        val_miss,
        var_miss,
    ):
        self.pattern = pattern
        self.algo = algo
        self.val_hits = val_hits
        self.var_hits = var_hits
        self.val_miss = val_miss
        self.var_miss = var_miss


class DataPoint:
    def __init__(
        self, pattern: str, algo: str, val_hits, var_hits, val_miss, var_miss, ratio
    ):
        self.pattern = pattern
        self.algo = algo
        self.val_hits = val_hits
        self.var_hits = var_hits
        self.val_miss = val_miss
        self.var_miss = var_miss
        self.miss_ratio = ratio

    def __str__(self):
        return f"""{self.algo}-{self.pattern}:
\t{self.miss_ratio}
Hits:\n\t{self.val_hits}\t\t{self.var_hits}
Misses:\n\t{self.val_miss}\t\t{self.var_miss}
========================\n"""


BASE_PATH = path.join("../", "out/miss-ratio")

all_trials: [Trial] = []
all_mem_patterns = set()
all_algorithms = set()
trial_averages: [TrialAverage] = []
data_points: [DataPoint] = []

# Raw data for all trials
for root, _, files in walk(BASE_PATH):
    if "stats.txt" not in files:
        continue

    stat_file = path.join(root, "stats.txt")
    f = open(stat_file, "r")
    lines = f.readlines()

    # print(stat_file)

    stats = dict()
    for stat in important_stats:
        # print(stat)
        # print(important_stats)
        stat_line = [line for line in lines if line.startswith(stat)][0]
        stat_line_words = stat_line.split()

        stat_name = stat_line_words[0]
        stat_name = str.removeprefix(stat_name, "system.cpu.dcache.overall")
        stat_name = str.removesuffix(stat_name, "::total")
        stat_name = str.lower(stat_name)
        try:
            stat = int(stat_line_words[1])
        except ValueError:
            stat = float(stat_line_words[1])

        stats[stat_name] = stat
    stats["miss-ratio"] = stats["misses"] / stats["accesses"]

    parent_dirs = root.split("/")
    if len(parent_dirs) < 7:
        continue
    # print(parent_dirs)
    # print(files)
    assoc = parent_dirs[3]
    pattern = parent_dirs[4]
    algo = parent_dirs[5]
    trial_num = parent_dirs[6]

    trial = Trial(assoc, pattern, algo, trial_num, stats)
    all_trials.append(trial)
    all_mem_patterns.add(pattern)
    all_algorithms.add(algo)

    f.close()

# Calculate mean/variance of hits and misses for all experiments
for mem_pattern in all_mem_patterns:
    for algorithm in all_algorithms:
        trials = [
            t.stats
            for t in all_trials
            if t.mem_pattern == mem_pattern and t.algo == algorithm
        ]

        hits = np.array([d["hits"] for d in trials])
        misses = np.array([d["misses"] for d in trials])
        accesses = np.array([d["accesses"] for d in trials])

        mean_hits = np.mean(hits)
        mean_miss = np.mean(misses)
        mean_accesses = np.mean(accesses)

        var_hits = np.var(hits)
        var_miss = np.var(misses)
        var_accesses = np.var(accesses)

        # assert var_accesses == 0

        trial_avg = TrialAverage(
            mem_pattern, algorithm, mean_hits, var_hits, mean_miss, var_miss
        )
        trial_averages.append(trial_avg)

# Separating (by name) control runs from experiment runs
experiment_mem_patterns = set(
    [p for p in all_mem_patterns if not p.endswith("-control")]
)
control_mem_patterns = all_mem_patterns.difference(experiment_mem_patterns)

# Normalizing data by subtracting control from experiment data
# Resulting number of hits is only from the memory access portions
for mem_pattern in experiment_mem_patterns:
    for algorithm in all_algorithms:
        trial_avg = [
            t
            for t in trial_averages
            if t.pattern == mem_pattern and t.algo == algorithm
        ][0]
        control_avg = [
            t
            for t in trial_averages
            if t.pattern == (mem_pattern + "-control") and t.algo == algorithm
        ][0]

        norm_val_hits = trial_avg.val_hits - control_avg.val_hits
        norm_var_hits = trial_avg.var_hits + control_avg.var_hits
        norm_val_miss = trial_avg.val_miss - control_avg.val_miss
        norm_var_miss = trial_avg.var_miss + control_avg.var_miss
        ratio = norm_val_miss / (norm_val_miss + norm_val_hits)
        point = DataPoint(
            mem_pattern,
            algorithm,
            norm_val_hits,
            norm_var_hits,
            norm_val_miss,
            norm_var_miss,
            ratio,
        )
        data_points.append(point)

for trial in all_trials:
    trial_str = "{},{},{},{},{},{},{},{}\n".format(
        trial.assoc,
        trial.algo,
        trial.mem_pattern,
        trial.trial_num,
        trial.stats["accesses"],
        trial.stats["hits"],
        trial.stats["misses"],
        trial.stats["miss-ratio"],
    )
    out_file.write(trial_str)

out_file.close()
