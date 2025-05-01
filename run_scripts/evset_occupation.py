import argparse
import os
import subprocess
from time import sleep

NUM_TRIALS = 64

access_pattern_tags = {"s": "sequential", "d": "double", "r": "repeat", "?": "random"}

repl_tags = {"s": "SIEVE", "t": "TreePLRU", "3": "3Tree", "2": "2Tree", "?": "RR"}

access_patterns = {
    "s": [],  # Sequential
    "d": [],  # Double
    "r": [3, 4, 5],  # Repeat
    # "z": [0.9, 0.8, 0.7, 0.6],  # Zipf-random
}

replacement_policies = {
    "s": [],  # SIEVE
    "3": [],
    # "2": [  # SPLRU
    #     cold + hot + choice
    #     for cold in ["r", "l", "f"]
    #     for hot in ["r", "l", "f"]
    #     for choice in ["h", "q", "e", "n"]
    # ],
    "t": [],  # TreePLRU
    # "2": [],  # 2Q (defunct)
    "?": [],  # Random
}

assocs = [
    # 2,
    16,
    8,
    4,
]

parser = argparse.ArgumentParser(
    prog="Eviction testing runner",
    description="Running the eviction testing simulation and storing the results",
)
parser.add_argument("-f", "--file")

print("about to parse args")

args = parser.parse_args()

abs_path = os.path.abspath(args.file)
print(abs_path)
f = None
if not os.path.isfile(abs_path):
    print("File does not exist, creating new file", args.file)
    f = open(args.file, "a")
    f.write("Replacement, Access Pattern, Associativity, Touches\n")
else:
    print("File does not exist, appending to  q", args.file)
    f = open(args.file, "a")

for pat, pat_args in access_patterns.items():
    for repl, repl_args in replacement_policies.items():
        for assoc in assocs:
            command = [
                "attack_sim/build/occupation",
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
                        print("=" * 24)
                        print(
                            f"ERROR: Test failed with RC {res_rc}\nReplacement:\t{repl}-{repl_args}\nAccess Pattern:\t{pat}-{pat_args}\nAssociativity:\t{assoc}"
                        )
                        print(f"Command:\t{c[0]}")
                        print("=" * 24)
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
