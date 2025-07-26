import os
from os import path, listdir

important_lines = [
    "system.cpu.dcache.overallHits::total",
    "system.cpu.dcache.overallMisses::total",
    "system.cpu.dcache.overallAccesses::total",
    # Does not make sense to compare this between accessing vs. control
    # Calculate miss rate based on hit and miss numbers
    # "system.cpu.dcache.overallMissRate::total",
]


class Trial:
    def __init__(self, pattern: str, algo: str, stats: dict, trial_num: int):
        self.mem_pattern = pattern
        self.algo = algo
        self.stats = stats
        self.trial_num = trial_num


base_path = os.path.join("../", "out/miss-ratio")

print(base_path)

all_pattern_paths = [
    f for f in listdir(base_path) if not path.isfile(path.join(base_path, f))
]

print(all_pattern_paths)

pattern_paths = [p for p in all_pattern_paths if not p.endswith("-control")]
control_paths = [p + "-control" for p in pattern_paths]

print(pattern_paths)
print(control_paths)

all_trials: [Trial] = []
pattern_data = dict()

# Read all output file data into a raw data structure
for pattern_path, control_path in zip(pattern_paths, control_paths):
    pat_path = path.join(base_path, pattern_path)
    algo_paths = [
        f for f in listdir(pat_path) if not path.isfile(path.join(pat_path, f))
    ]

    print(algo_paths)

    algo_data = dict()

    for algo in algo_paths:
        algo_dir = path.join(base_path, pattern_path, algo)
        control_dir = path.join(base_path, control_path, algo)
        algo_f = open(path.join(algo_dir, "stats.txt"), "r")
        control_f = open(path.join(control_dir, "stats.txt"), "r")

        algo_lines = algo_f.readlines()
        control_lines = control_f.readlines()

        normalized_data = dict()
        for stat in important_lines:
            algo_stat_line = [line for line in algo_lines if line.startswith(stat)][0]
            control_stat_line = [
                line for line in control_lines if line.startswith(stat)
            ][0]
            # print(algo_stat_line)
            # print(control_stat_line)
            # print(int(algo_stat_line.split()[1]))
            try:
                algo_stat = int(algo_stat_line.split()[1])
                control_stat = int(control_stat_line.split()[1])
            except ValueError:
                algo_stat = float(algo_stat_line.split()[1])
                control_stat = float(control_stat_line.split()[1])
            sanitized_stat = str.removeprefix(stat, "system.cpu.dcache.overall")
            sanitized_stat = str.removesuffix(sanitized_stat, "::total")
            sanitized_stat = str.lower(sanitized_stat)
            normalized_data[sanitized_stat] = algo_stat - control_stat
        #             print(
        #                 f"{stat}:\
        # \n\t{normalized_data[stat]}"
        #             )

        normalized_data["miss_ratio"] = (
            normalized_data["misses"] / normalized_data["accesses"]
        )
        algo_data[algo] = normalized_data

    pattern_data[pattern_path] = algo_data

for pattern, pat_data in pattern_data.items():
    for algo, algo_data in pat_data.items():
        print(algo)
        print(algo_data)
    pass
