import argparse
import os
import subprocess
from time import sleep

NUM_TRIALS = 64

access_pattern_tags = {"s": "sequential", "d": "double", "r": "repeat", "?": "random"}

repl_tags = {"s": "SIEVE", "t": "TreePLRU", "2": "TwoQ", "?": "RR"}

access_patterns = {
    "s": [],  # SIEVE
    "q": [  # SPLRU
        cold + hot + choice
        for cold in ["r", "l", "f"]
        for hot in ["r", "l", "f"]
        for choice in ["h", "q", "e", "n"]
    ],
    # "d": [],
    # "r": [3, 4, 5],
    # "z": [0.9, 0.8, 0.7, 0.6],
}

replacement_policies = {
    # "s": [],
    "t": [],
    # "2": [],
    # "?": []
}

assocs = [
    # 2,
    4,
    8,
    16,
]

parser = argparse.ArgumentParser(
    prog="Eviction testing runner",
    description="Running the eviction testing simulation and storing the results",
)
parser.add_argument("-f", "--file")
args = parser.parse_args()

abs_path = os.path.abspath(args.file)
f = None
if not os.path.isfile(abs_path):
    f = open(args.file, "a")
    f.write("Replacement, Access Pattern, Associativity, Touches\n")
else:
    f = open(args.file, "a")

for pat, pat_args in access_patterns.items():
    for repl, repl_args in replacement_policies.items():
        for assoc in assocs:
            command = [
                "eviction/build/occupation",
                str(assoc),  # Associativity
                str(assoc),  # Memory region size, assume minimal evsets
                repl,
                pat,
            ]

            # Handle multiple possible argument variants
            commands = []
            if len(repl_args) == 0 and len(pat_args) == 0:
                commands.append((command, None, None))
            elif len(repl_args) == 0:
                for pat_arg in pat_args:
                    c = command[:]
                    c.append(str(pat_arg))
                    commands.append((c, None, str(pat_arg)))
            elif len(pat_args) == 0:
                for repl_arg in repl_args:
                    c = command[:]
                    c.append(repl_arg)
                    commands.append((c, str(repl_arg), None))
            else:
                for repl_arg in repl_args:
                    for pat_arg in pat_args:
                        c = command[:]
                        c.append(repl_arg)
                        c.append(str(pat_arg))
                        commands.append((c, str(repl_arg), str(pat_arg)))
            print(
                f"Starting simulation:\n{repl_tags[repl]}-{repl_args}\n{access_pattern_tags[pat]}-{pat_args}\n{assoc}"
            )

            for trial in range(NUM_TRIALS):
                for c in commands:
                    res = subprocess.run(c[0], stdout=subprocess.PIPE)
                    res_rc = res.returncode
                    if res_rc != 0:
                        print(
                            f"ERROR: Test failed with RC {res_rc}\nReplacement: {repl}-{repl_args}\nAccess Pattern:{pat}-{pat_args}\nAssociativity: {assoc}"
                        )
                        exit(1)
                    res_int = int(res.stdout.decode("utf-8"))

                    # CSV formatting and logging
                    repl_tag = repl_tags[repl]
                    pat_tag = access_pattern_tags[pat]
                    if c[1] is not None:
                        repl_tag = repl_tag + "-" + c[1]
                    if c[2] is not None:
                        pat_tag = pat_tag + "-" + c[2]
                    csv_line = f"{repl_tag}, {pat_tag}, {assoc}, {res_int}\n"
                    _ = f.write(csv_line)

                sleep(0.01)
            print("Finished simulation\n----------------")
