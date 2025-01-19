"""
Script to run SPEC CPU2017 benchmarks with gem5.
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
    DiskImageResource,
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
    coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL,
    kvm_required=True,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="gem5 config file to run SPEC benchmarks"
    )
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Input the full path to the built spec-2017 disk-image.",
    )

    parser.add_argument(
        "--partition",
        type=str,
        required=False,
        default=None,
        help='Input the root partition of the SPEC disk-image. If the disk is \
        not partitioned, then pass "".',
    )

    parser.add_argument(
        "--benchmark",
        type=str,
        required=True,
        help="Input the benchmark program to execute.",
    )

    parser.add_argument(
        "--size",
        type=str,
        required=True,
        help="Sumulation size the benchmark program.",
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

    args = parser.parse_args()

    if args.image[0] != "/":
        # We need to get the absolute path to this file. We assume that the file is
        # present on the current working directory.
        args.image = os.path.abspath(args.image)

    if not os.path.exists(args.image):
        warn("Disk image not found!")
        print("Instructions on building the disk image can be found at: ")
        print("https://gem5art.readthedocs.io/en/latest/tutorials/spec-tutorial.html")
        fatal(f"The disk-image is not found at {args.image}")

    return args
    # parser.add_argument("kernel", type=str, help="Path to vmlinux")
    # parser.add_argument(
    #     "disk", type=str, help="Path to the disk image containing SPEC benchmarks"
    # )
    # parser.add_argument("cpu", type=str, help="Name of the detailed CPU")
    # parser.add_argument("benchmark", type=str, help="Name of the SPEC benchmark")
    # parser.add_argument("size", type=str, help="Available sizes: test, train, ref")
    # parser.add_argument(
    #     "-k",
    #     "--kernel",
    #     type=str,
    #     default="linux-4.19.83/vmlinux-4.19.83",
    #     help="Path to vmlinux",
    # )
    # parser.add_argument(
    #     "-l",
    #     "--no-copy-logs",
    #     default=False,
    #     action="store_true",
    #     help="Not copy SPEC run logs to the host system;" "Logs are copied by default",
    # )
    # parser.add_argument(
    #     "-z",
    #     "--allow-listeners",
    #     default=False,
    #     action="store_true",
    #     help="Turn on ports;" "The ports are off by default",
    # )
    # return parser.parse_args()


def create_cache_hierarchy(assoc: int, repl: str):
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

    cache_hierarchy = PrivateL1CacheHierarchy(
        l1d_size="32KiB",
        l1i_size="32KiB",
        assoc=assoc,
        repl=ret,
    )
    return cache_hierarchy


def handle_finish_boot():
    print("Done booting Linux")
    print("Resetting stats at start of ROI")
    m5.stats.reset()
    processors.switch()
    yield False
    print("Dump stats at end fo ROI")
    m5.stats.dump()
    yield True


if __name__ == "__m5_main__":
    print("Starting run script")
    args = parse_arguments()

    image = args.image
    benchmark = args.benchmark
    size = args.size
    partition = args.partition
    assoc = args.assoc
    repl = args.repl

    cache_hierarchy = create_cache_hierarchy(assoc, repl)

    processors = SimpleSwitchableProcessor(
        starting_core_type=CPUTypes.KVM,
        switch_core_type=CPUTypes.TIMING,
        isa=ISA.X86,
        num_cores=1,
    )

    memory = DualChannelDDR4_2400(size="3GiB")

    board = X86Board(
        clk_freq="3GHz",
        processor=processors,
        memory=memory,
        cache_hierarchy=cache_hierarchy,
    )

    output_dir = f"{benchmark}/{repl}_{assoc}"
    try:
        os.makedirs(os.path.join(m5.options.outdir, output_dir))
    except FileExistsError:
        warn("output directory already exists!")

    command = "m5 exit;" \
        + "echo 'This is running on Timing CPU cores.';" \
        + "sleep 1;" \
        + "m5 exit;"
    board.set_kernel_disk_workload(
        kernel=obtain_resource("x86-linux-kernel-5.4.49"),
        # SPEC CPU workload disk image
        disk_image=DiskImageResource(args.image, root_partition=args.partition),
        readfile_contents=command,
    )

    simulator = Simulator(
        board=board,
        on_exit_event={
            ExitEvent.EXIT: (func() for func in [processors.switch]),
        },
    )

    globalStart = time.time()

    print("Starting simulation...")
    m5.stats.reset()
    simulator.run()

    globalEnd = time.time()

    print("Finished simulation")

    roi_begin_ticks = simulator.get_tick_stopwatch()[0][1]
    roi_end_ticks = simulator.get_tick_stopwatch()[1][1]
    print("ROI simulated ticks: " + str(roi_end_ticks - roi_begin_ticks))
    print(
        "Run time: %.2fs:%.2fs"
        % ((globalEnd - globalStart / 60), globalEnd - globalStart)
    )
    print("Simulated time:", str(simulator.get_current_tick() / 1e12), "sec")
