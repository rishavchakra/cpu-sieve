import argparse

from gem5.utils.requires import requires
from gem5.components.boards.x86_board import X86Board
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.cachehierarchies.classic.research_cache_hierarchy import (
    ResearchCacheHierarchy,
)
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.processors.simple_switchable_processor import (
    SimpleSwitchableProcessor,
)
from gem5.components.processors.simple_processor import SimpleProcessor

# from gem5.coherence_protocol import CoherenceProtocol
from gem5.isas import ISA
from gem5.components.processors.cpu_types import CPUTypes
from gem5.resources.resource import Resource
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator
from gem5.simulate.exit_event import ExitEvent

requires(
    isa_required=ISA.X86,
    # coherence_protocol_required=CoherenceProtocol.MESI_TWO_LEVEL,
    kvm_required=True,
)


def get_args():
    p = argparse.ArgumentParser(description="PARSEC Simulation setup and running")
    p.add_argument(
        "--outjson",
        action="store",
        type=str,
        help="File path to save JSON simulation data",
    )
    p.add_argument(
        "--checkpoint-dir",
        action="store",
        type=str,
        default="out/trace/checkpoint",
        help="Directory with a checkpoint to restore from",
    )
    p.add_argument(
        "--save-checkpoint",
        action="store_true",
        help="Save a checkpoint after Linux boot",
    )
    p.add_argument(
        "--restore-checkpoint",
        action="store",
        type=str,
        default="out/trace/checkpoint",
        help="Restore a checkpoint at the end of Linux boot",
    )
    p.add_argument(
        "--trace-directory",
        action="store",
        type=str,
        help="Directory with trace files to restore from",
    )
    p.add_argument(
        "--benchmark",
        type=str,
        help="PARSEC benchmark to execute",
    )
    p.add_argument("--repl", action="store", type=str, help="Cache replacement policy")
    p.add_argument("--assoc", action="store", type=str, help="Cache associativity")
    return p.parse_args()


def get_cache_hierarchy(is_save_checkpoint, repl, assoc):
    if is_save_checkpoint:
        return NoCache()
    return ResearchCacheHierarchy(
        l1_size="32KiB",
        l1_assoc=int(assoc),
        repl=repl,
    )


def get_processor(is_save_checkpoint, is_restore_checkpoint):
    if is_save_checkpoint:
        proc = SimpleSwitchableProcessor(
            starting_core_type=CPUTypes.KVM,
            switch_core_type=CPUTypes.O3,
            num_cores=2,
        )
        for p in proc.start:
            proc.core.usePerf = False
        return proc
    if is_restore_checkpoint:
        proc = SimpleProcessor(
            cpu_type=CPUTypes.ATOMIC,
            num_cores=1,
            isa=ISA.X86,
        )


def get_command(is_save_checkpoint, benchmark):
    if is_save_checkpoint:
        return "m5 exit; m5 checkpoint; m5 exit;"
    return (
        "cd /home/gem5/parsec-benchmark;"
        + "source env.sh;"
        + f"parsecmgmt -a run -p {benchmark} -c gcc-hooks -i simsmall -n 2;"
        + "sleep 5;"
        + "m5 exit;"
    )


def get_disk_image(is_save_checkpoint):
    # if is_save_checkpoint:
    #     return obtain_resource("x86-ubuntu-18.04-img")
    # else:
    return obtain_resource("x86-parsec")


def handle_workbegin():
    print("Done booting Linux")
    print()


def get_simulator(board, is_save_checkpoint, checkpoint_dir):
    pass


def setup_fs_simulation(
    processor,
    cache,
    command,
    disk_image,
    is_restore_checkpoint,
    checkpoint_dir,
    json_outpath,
):
    memory = SingleChannelDDR3_1600(size="2GiB")
    board = X86Board(
        clk_freq="3GHz",
        processor=processor,
        memory=memory,
        cache_hierarchy=cache,
    )
    board.set_kernel_disk_workload(
        kernel=Resource(
            "x86-linux-kernel-5.4.49",
        ),
        disk_image=disk_image,
        readfile_contents=command,
    )
    if is_restore_checkpoint:
        simulator = Simulator(
            board=board,
            on_exit_event={
                ExitEvent.EXIT: (func() for func in [processor.switch]),
            },
            checkpoint_path=checkpoint_dir,
        )
        simulator.add_json_stats_output(json_outpath)
        return simulator
    else:
        simulator = Simulator(
            board=board,
            on_exit_event={
                ExitEvent.EXIT: (func() for func in [processor.switch]),
            },
        )
        simulator.add_json_stats_output(json_outpath)
        return simulator


args = get_args()
cache = get_cache_hierarchy(args.save_checkpoint, args.repl, args.assoc)
processor = get_processor(args.save_checkpoint, args.restore_checkpoint)
command = get_command(args.save_checkpoint, args.benchmark)
disk_image = get_disk_image(args.save_checkpoint)
simulation = setup_fs_simulation(
    processor,
    cache,
    command,
    disk_image,
    args.restore_checkpoint,
    args.checkpoint_dir,
    args.outjson,
)

simulation.run()
