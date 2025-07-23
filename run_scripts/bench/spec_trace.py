# Copyright (c) 2023 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

This script demonstrates how to use KVM CPU without perf.
This simulation boots Ubuntu 18.04 using 2 KVM CPUs without using perf.

Usage
-----

```
scons build/X86/gem5.opt -j`nproc`
./build/X86/gem5.opt configs/example/gem5_library/x86-ubuntu-run-with-kvm-no-perf.py
```
"""

import argparse
import os
from os import warn
import time
import m5
from gem5.utils.requires import requires
from gem5.components.boards.x86_board import X86Board
from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
from gem5.components.processors.simple_switchable_processor import (
    SimpleSwitchableProcessor,
)
from gem5.resources.resource import (
    DiskImageResource,
    obtain_resource,
)
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.coherence_protocol import CoherenceProtocol
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent
from gem5.resources.workload import Workload

# This simulation requires using KVM with gem5 compiled for X86 simulation
# and with MESI_Two_Level cache coherence protocol.
requires(
    isa_required=ISA.X86,
    coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL,
    kvm_required=True,
)

benchmark_choices = [
    "500.perlbench_r",
    "502.gcc_r",
    "503.bwaves_r",
    "505.mcf_r",
    "507.cactusBSSN_r",
    "508.namd_r",
    "510.parest_r",
    "511.povray_r",
    "519.lbm_r",
    "520.omnetpp_r",
    "521.wrf_r",
    "523.xalancbmk_r",
    "525.x264_r",
    "527.cam4_r",
    "531.deepsjeng_r",
    "538.imagick_r",
    "541.leela_r",
    "544.nab_r",
    "548.exchange2_r",
    "549.fotonik3d_r",
    "554.roms_r",
    "557.xz_r",
    "600.perlbench_s",
    "602.gcc_s",
    "603.bwaves_s",
    "605.mcf_s",
    "607.cactusBSSN_s",
    "608.namd_s",
    "610.parest_s",
    "611.povray_s",
    "619.lbm_s",
    "620.omnetpp_s",
    "621.wrf_s",
    "623.xalancbmk_s",
    "625.x264_s",
    "627.cam4_s",
    "631.deepsjeng_s",
    "638.imagick_s",
    "641.leela_s",
    "644.nab_s",
    "648.exchange2_s",
    "649.fotonik3d_s",
    "654.roms_s",
    "996.specrand_fs",
    "997.specrand_fr",
    "998.specrand_is",
    "999.specrand_ir",
]

size_choices = ["test", "train", "ref"]


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="SPEC benchmark trace generation arguments"
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
        choices=benchmark_choices,
    )
    parser.add_argument(
        "--size",
        type=str,
        required=True,
        help="Sumulation size the benchmark program.",
        choices=size_choices,
    )
    args = parser.parse_args()
    return args


cache_hierarchy = MESITwoLevelCacheHierarchy(
    l1d_size="32KiB",
    l1d_assoc=8,
    l1i_size="32KiB",
    l1i_assoc=8,
    l2_size="256KiB",
    l2_assoc=16,
    num_l2_banks=2,
)

args = parse_arguments()

if args.image[0] != "/":
    # We need to get the absolute path to this file. We assume that the file is
    # present on the current working directory.
    args.image = os.path.abspath(args.image)

# Main memory
memory = SingleChannelDDR4_2400(size="3GiB")

# This is a switchable CPU. We first boot Ubuntu using KVM, then the guest
# will exit the simulation by calling "m5 exit" (see the `command` variable
# below, which contains the command to be run in the guest after booting).
# Upon exiting from the simulation, the Exit Event handler will switch the
# CPU type (see the ExitEvent.EXIT line below, which contains a map to
# a function to be called when an exit event happens).
processor = SimpleSwitchableProcessor(
    starting_core_type=CPUTypes.KVM,
    switch_core_type=CPUTypes.TIMING,
    isa=ISA.X86,
    num_cores=1,
)

# Here we tell the KVM CPU (the starting CPU) not to use perf.
for proc in processor.start:
    proc.core.usePerf = False

# Here we setup the board. The X86Board allows for Full-System X86 simulations.
board = X86Board(
    clk_freq="3GHz", processor=processor, memory=memory, cache_hierarchy=cache_hierarchy
)

# Here we set the Full System workload.
# The `set_kernel_disk_workload` function for the X86Board takes a kernel, a
# disk image, and, optionally, a command to run.

# This is the command to run after the system has booted. The first `m5 exit`
# will stop the simulation so we can switch the CPU cores from KVM to timing
# and continue the simulation to run the echo command, sleep for a second,
# then, again, call `m5 exit` to terminate the simulation. After simulation
# has ended you may inspect `m5out/system.pc.com_1.device` to see the echo
# output.
# command = (
#     "m5 checkpoint;"
#     + "m5 exit;"
#     + "echo 'This is running on Timing CPU cores.';"
#     + "sleep 1;"
#     + "m5 exit;"
# )

output_dir = "speclogs_" + "".join(x.strip() for x in time.asctime().split())
output_dir = output_dir.replace(":", "")

# We create this folder if it is absent.
try:
    os.makedirs(os.path.join(m5.options.outdir, output_dir))
except FileExistsError:
    warn("output directory already exists!")

command = f"{args.benchmark} {args.size} {output_dir}"

board.set_kernel_disk_workload(
    # The x86 linux kernel will be automatically downloaded to the
    # `~/.cache/gem5` directory if not already present.
    # SPEC CPU2017 benchamarks were tested with kernel version 4.19.83
    kernel=obtain_resource("x86-linux-kernel-4.19.83"),
    # The location of the x86 SPEC CPU 2017 image
    disk_image=DiskImageResource(args.image, root_partition=args.partition),
    readfile_contents=command,
)

simulator = Simulator(
    board=board,
    on_exit_event={
        # Here we want override the default behavior for the first m5 exit
        # exit event. Instead of exiting the simulator, we just want to
        # switch the processor. The 2nd m5 exit after will revert to using
        # default behavior where the simulator run will exit.
        ExitEvent.EXIT: (func() for func in [processor.switch])
    },
)
simulator.run()
