import argparse
import os
import subprocess
from time import sleep

NUM_TRIALS = 64

access_pattern_tags = {"s": "sequential", "d": "double", "r": "repeat", "?": "random"}

repl_tags = {"s": "SIEVE", "t": "TreePLRU", "2": "TwoQ", "?": "RR"}

access_patterns = {
    "s": [],
    "d": [],
    "r": [3, 4, 5],
    "z": [0.9, 0.8, 0.7, 0.6],
}

replacement_policies = {
    "s": [],  # SIEVE
    "t": [],  # TreePLRU
    # "2": [],  # 2Q
    "?": [],  # Random
    "q": [  # SPLRU
        cold + hot + choice
        for cold in ["r", "l", "f"]
        for hot in ["r", "l", "f"]
        for choice in ["h", "q", "e", "n"]
    ],
}

assocs = {
    2: [2],
    4: [4],
    8: [8],
    16: [16],
}

parser = argparse.ArgumentParser(
    prog="Bypass",
    description="Testing cache bypass with eviction sets simulation and storing the results",
)
parser.add_argument("-f", "--file")
args = parser.parse_args()

abs_path = os.path.abspath(args.file)
f = None
if not os.path.isfile(abs_path):
    f = open(args.file, "a")
    f.write("Replacement, Access Pattern, Associativity, Evset size, DRAM Hits\n")
else:
    f = open(args.file, "a")

for pat, pat_args in access_patterns.items():
    for repl, repl_args in replacement_policies.items():
        for assoc, assoc_args in assocs.items():
            command = [
                "eviction/build/bypass",
                str(assoc),
            ]

            commands = []
            if len(repl_args) == 0 and len(pat_args) == 0:
                for assoc_arg in assoc_args:
                    c = command[:]
                    c.append(str(assoc_arg))
                    commands.append((c, assoc_arg, None, None))
            elif len(repl_args) == 0:
                for pat_arg in pat_args:
                    for assoc_arg in assoc_args:
                        c = command[:]
                        c.append(str(assoc_arg))
                        c.append(str(pat_arg))
                        commands.append((c, assoc_arg, None, str(pat_arg)))
            elif len(pat_args) == 0:
                for repl_arg in repl_args:
                    for assoc_arg in assoc_args:
                        c = command[:]
                        c.append(str(assoc_arg))
                        c.append(str(repl_arg))
                        commands.append((c, assoc_arg, str(repl_arg), None))
            else:
                for repl_arg in repl_args:
                    for pat_arg in pat_args:
                        for assoc_arg in assoc_args:
                            c = command[:]
                            c.append(str(assoc_arg))
                            c.append(str(pat_arg))
                            c.append(str(repl_arg))
                            commands.append((c, assoc_arg, str(repl_arg), str(pat_arg)))

            print(
                f"Starting simulation:\n{repl_tags[repl]}-{repl_args}\n{access_pattern_tags[pat]}-{pat_args}\n{assoc}-{assoc_args}"
            )

            for trial in range(NUM_TRIALS):
                for c in commands:
                    res = subprocess.run(c[0], stdout=subprocess.PIPE)
                    res_rc = res.returncode
                    if res_rc != 0:
                        print(
                            f"ERROR: Test failed with RC {res_rc}\nReplacement: {repl}-{repl_args}\nAccess Pattern:{pat}-{pat_args}\nAssociativity: {assoc}-{assoc_args}"
                        )
                        exit(1)
                    res_int = int(res.stdout.decode("utf-8"))

                    evset_size = c[1]
                    repl_tag = repl_tags[repl]
                    pat_tag = access_pattern_tags[pat]
                    if c[2] is not None:
                        repl_tag = repl_tag + "-" + c[1]
                    if c[3] is not None:
                        pat_tag = pat_tag + "-" + c[2]
                    csv_line = (
                        f"{repl_tag}, {pat_tag}, {assoc}, {evset_size}, {res_int}\n"
                    )
                    _ = f.write(csv_line)
                sleep(0.01)
            print("Finished simulation\n----------------")
