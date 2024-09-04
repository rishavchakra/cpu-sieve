import subprocess
import os

access_patterns = [
    'seq',
    'seq-control',
    'zipf',
    'zipf-control'
]

replacement_policies = [
    'sieve',
    'lru',
    'fifo',
    'rr',
    'second-chance',
    'tree-plru',
    'weighted-lru',
]

for mem_pat in access_patterns:
    for repl_policy in replacement_policies:
        print(f'================================\n\
SIEVE SIMULATION\n\
Access pattern:{mem_pat}\n\
Replacement Policy:{repl_policy}')

        if os.path.exists(f'out/miss-ratio/{mem_pat}/{repl_policy}'):
            print('\nSimulation already completed!')
            continue

        _ = subprocess.run([
            'gem5/build/ALL/gem5.opt',
            '-d',
            f'out/miss-ratio/{mem_pat}/{repl_policy}',
            'gem5/configs/research/sieve/miss-ratio.py',
            '-m',
            mem_pat,
            '-r',
            repl_policy
        ])
