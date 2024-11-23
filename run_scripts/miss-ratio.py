import subprocess
import os

NUM_TRIALS = 32

# access_patterns = ["seq", "seq-control", "zipf", "zipf-control"]
access_patterns = ["zipf-control"]

replacement_policies = [
    # "sieve",
    # "tree-sieve",
    "lru",
    "fifo",
    "rr",
    # "second-chance",
    "tree-plru",
    # "weighted-lru",
]

for mem_pat in access_patterns:
    for repl_policy in replacement_policies:
        for log_assoc in range(1, 5):
            assoc = 2**log_assoc
            print(
                f"================================\n\
    SIEVE SIMULATION\n\
    Access pattern:     {mem_pat}\n\
    Replacement Policy: {repl_policy}\n\
    Associativity:      {assoc}\n"
            )

            # if os.path.exists(f'out/miss-ratio/{mem_pat}/{repl_policy}'):
            #     print('\nSimulation already completed!')
            #     continue

            for trial in range(NUM_TRIALS):
                _ = subprocess.run(
                    [
                        "gem5/build/X86/gem5.opt",
                        "-d",
                        f"out/miss-ratio/{assoc}/{mem_pat}/{repl_policy}/{trial}",
                        "gem5/configs/research/sieve/miss-ratio.py",
                        "-m",
                        mem_pat,
                        "-r",
                        repl_policy,
                        "-a",
                        str(assoc),
                    ]
                )
