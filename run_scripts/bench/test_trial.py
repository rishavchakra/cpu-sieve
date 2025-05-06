"""
Script to run test benchmarks with gem5.
"""

import argparse
import json
import os
import time

import m5
from m5.objects import *
from m5.stats.gem5stats import get_simstat
from m5.util import (
    fatal,
    warn,
)

from gem5.coherence_protocol import CoherenceProtocol
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_switchable_processor import (
    SimpleSwitchableProcessor,
)
from gem5.isas import ISA
from gem5.resources.resource import (
    Resource,
    obtain_resource,
)
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import (
    PrivateL1CacheHierarchy,
)

requires(
    isa_required=ISA.X86,
    kvm_required=True,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="gem5 config file to run PARSEC benchmarks"
    )

    parser.add_argument(
        "--assoc",
        type=int,
        required=True,
        help="Associativity of cache",
        choices=[1, 2, 4, 8, 16, 32],
    )

    parser.add_argument(
        "--repl",
        type=str,
        required=True,
        help="Replacement Policy of cache",
    )

    parser.add_argument(
        "--variant",
        type=str,
        required=False,
        help="Optional Replacement Policy Variant string",
    )

    args = parser.parse_args()

    return args


def create_cache_hierarchy(assoc: int, repl: str, variant: str | None):
    # For simplicity, we only use one level of cache hierarchy
    # Create an L1 instruction and data cache
    ret = None
    match repl:
        case "sieve":
            ret = SIEVERP()
        case "rr":
            ret = RandomRP()
        case "fifo":
            ret = FIFORP()
        case "lru":
            ret = LRURP()
        case "second-chance":
            ret = SecondChanceRP()
        case "tree-plru":
            ret = TreePLRURP()
        case "rrip":
            ret = RRIPRP()
        case "brrip":
            ret = BRRIPRP()
        case "nru":
            ret = NRURP()
        case "2tree":
            if variant is None:
                print("WARNING: Initializing 2Tree with no parameters")
                ret = TwoTreeRP(cold_repl=0, hot_repl=0, probation_type=0)
            else:
                cold_repl = 0
                hot_repl = 0
                probation_type = 0

                if variant[0] == "l":
                    cold_repl = 1
                elif variant[0] == "f":
                    cold_repl = 2

                if variant[1] == "l":
                    hot_repl = 1
                elif variant[1] == "f":
                    hot_repl = 2

                if variant[2] == "h":
                    probation_type = 1
                elif variant[2] == "q":
                    probation_type = 2
                elif variant[2] == "e":
                    probation_type = 3

                ret = TwoTreeRP(
                    cold_repl=cold_repl,
                    hot_repl=hot_repl,
                    probation_type=probation_type,
                )
        case "3tree":
            ret = ThreeTreeRP()

    cache_hierarchy = PrivateL1CacheHierarchy(
        l1d_size="32KiB",
        l1i_size="32KiB",
        assoc=assoc,
        replacement_policy=ret,
    )
    return cache_hierarchy


def handle_workbegin(processor):
    print("Boot finished, resetting stats")
    m5.stats.reset()
    processor.switch()
    yield False


def handle_workend():
    print("ROI finished, dumping stats")
    m5.stats.dump()
    yield True


if __name__ == "__m5_main__":
    print("Starting run script")
    args = parse_arguments()

    assoc = args.assoc
    repl = args.repl
    variant = args.variant

    cache_hierarchy = create_cache_hierarchy(assoc, repl, variant)

    processor = SimpleSwitchableProcessor(
        starting_core_type=CPUTypes.KVM,
        switch_core_type=CPUTypes.TIMING,
        isa=ISA.X86,
        num_cores=1,
    )

    for proc in processor.start:
        proc.core.usePerf = False

    memory = DualChannelDDR4_2400(size="3GiB")

    board = X86Board(
        clk_freq="3GHz",
        processor=processor,
        memory=memory,
        cache_hierarchy=cache_hierarchy,
    )

    try:
        os.makedirs(m5.options.outdir)
    except FileExistsError:
        warn("output directory already exists!")

    binary = "tests/test-progs/hello/bin/x86/linux/hello"
    system.workload = SEWorkload.init_compatible(binary)

    simulator = Simulator(
        board=board,
        on_exit_event={
            ExitEvent.WORKBEGIN: handle_workbegin(processor),
            ExitEvent.WORKEND: handle_workend(),
        },
    )

    globalStart = time.time()

    print("Running simulation")

    m5.stats.reset()

    simulator.run()

    print("Simulation successful")

    globalEnd = time.time()
    print("Finished simulation")
    print("ROI simulated time: " + (str(simulator.get_roi_ticks()[0])))
    print(
        "CPU simulation time: ",
        simulator.get_current_tick() / 1e12,
        "simulated seconds",
    )
    print(
        "Run time: %.2fs:%.2fs"
        % ((globalEnd - globalStart / 60), globalEnd - globalStart)
    )
    print("Simulated time:", str(m5.curTick() / 1e12), "sec")
