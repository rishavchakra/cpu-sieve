import subprocess

replacement_policies = {
    "sieve": [],
    # "tree-sieve": [],
    # "lru": [],
    # "fifo": [],
    "rr": [],
    # "second-chance": [],
    "tree-plru": [],
    # "weighted-lru": [],
    "rrip": [],
    "brrip": [],
    "nru": [],
    "2tree": [
        cold + hot + choice
        for cold in ["r", "l", "f"]
        for hot in ["r", "l", "f"]
        # for choice in ["h", "q", "e", "n"]
        for choice in ["n"]
    ],
    "3tree": [],
}

assocs = [
    16,
    8,
    4,
]

labels: list[str] = []
commands: list[str] = []

for assoc in assocs:
    for repl_policy, repl_args in replacement_policies.items():
        labels.append(
            f"================================\n\
TEST GEM5 SIMULATION\n\
Replacement Policy: {repl_policy}\n\
Associativity:      {assoc}\n"
        )

        # If linux with KVM enabled: switch 'atomic' 7 lines down to 'kvm'
        command = [
            "gem5/build/ALL/gem5.opt",
            f"-d out/gem5_test/{repl_policy}/{assoc}",
            "run_scripts/bench/test_trial.py",
            f"--assoc {str(assoc)}",
            f"--repl {repl_policy}",
        ]
        if len(repl_args) > 0:
            for repl_arg in repl_args:
                arg_command = command[:]
                arg_command[1] = f"-d out/gem5_test/{repl_policy}-{repl_arg}/{assoc}"
                arg_command.append(f"--variant {repl_arg}")
                commands.append(" ".join(arg_command))
        else:
            commands.append(" ".join(command))

cpus = 16
while len(commands) > 0:
    command_batch = commands[:cpus]
    label_batch = labels[:cpus]
    for label in label_batch:
        print(label)
    procs = [subprocess.Popen(cmd, shell=True) for cmd in command_batch]
    for p in procs:
        _ = p.wait()
    commands = commands[cpus:]
    labels = labels[cpus:]
