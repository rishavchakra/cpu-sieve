from itertools import starmap
from itertools import product
import os
import sys
from uuid import UUID

from gem5art.artifact import Artifact
from gem5art.run import gem5Run
from gem5art.tasks.tasks import run_job_pool
import multiprocessing as mp

experiments_repo = Artifact.registerArtifact(
    command="""
        git clone https://github.com/rishavchakra/cpu-sieve
        cd gem5-resources
    """,
    typ="git repo",
    name="spec2017 Experiment",
    path="./",
    cwd="./",
    documentation="""
        Main research repo with all experiments and scripts.
        Resources cloned from https://github.com/rishavchakra/cpu-sieve at branch main
    """,
)

gem5_repo = Artifact.registerArtifact(
    command="""
        git clone -b sieve-research https://github.com/rishavchakra/gem5
        cd gem5
        scons build/X86/gem5.fast -j16
    """,
    typ="git repo",
    name="gem5",
    path="gem5/",
    cwd="./",
    documentation="cloned gem5 at sieve-research branch",
)

gem5_binary = Artifact.registerArtifact(
    command="scons build/X86/gem5.fast -j16",
    typ="gem5 binary",
    name="gem5-20.1.0.4",
    cwd="gem5/",
    path="gem5/build/X86/gem5.opt",
    inputs=[
        gem5_repo,
    ],
    documentation="compiled gem5 v20.1.0.4 binary",
)

m5_binary = Artifact.registerArtifact(
    command="scons build/x86/out/m5",
    typ="binary",
    name="m5",
    path="gem5/util/m5/build/x86/out/m5",
    cwd="gem5/util/m5",
    inputs=[
        gem5_repo,
    ],
    documentation="m5 utility",
)

packer = Artifact.registerArtifact(
    command="""
        wget https://releases.hashicorp.com/packer/1.6.6/packer_1.6.6_linux_amd64.zip;
        unzip packer_1.6.6_linux_amd64.zip;
    """,
    typ="binary",
    name="packer",
    path="bench/packer",
    cwd="bench",
    documentation="Program to build disk images. Downloaded from https://www.packer.io/.",
)

disk_image = Artifact.registerArtifact(
    command="./packer build spec-2017/spec-2017.json",
    typ="disk image",
    name="spec-2017",
    cwd="bench/",
    path="bench/spec-2017/spec-2017-image/spec-2017",
    inputs=[
        packer,
        experiments_repo,
        m5_binary,
    ],
    documentation="Ubuntu Server with SPEC 2017 installed, m5 binary installed and root auto login",
)

linux_binary = Artifact.registerArtifact(
    name="vmlinux-4.19.83",
    typ="kernel",
    path="./vmlinux-4.19.83",
    cwd="./",
    command=""" wget http://dist.gem5.org/dist/v21-1/kernels/x86/static/vmlinux-4.19.83""",
    inputs=[
        experiments_repo,
    ],
    documentation="kernel binary for v4.19.83",
)

run_script_repo = Artifact.registerArtifact(
    command="""
        wget https://raw.githubusercontent.com/rishavchakra/cpu-sieve/main/bench/configs/run_spec.py
        mkdir -p system
        cd system
        wget https://raw.githubusercontent.com/rishavchakra/cpu-sieve/main/bench/configs/system/__init__.py
        wget https://raw.githubusercontent.com/rishavchakra/cpu-sieve/main/bench/configs/system/caches.py
        wget https://raw.githubusercontent.com/rishavchakra/cpu-sieve/main/bench/configs/system/fs_tools.py
        wget https://raw.githubusercontent.com/rishavchakra/cpu-sieve/main/bench/configs/system/system.py
    """,
    typ="git repo",
    name="configs",
    path="configs",
    cwd="./",
    documentation="gem5 run scripts made specifically for SPEC benchmarks",
)


def create_run(bench, repl, assoc):
    return gem5Run.createFSRun(
        # "3Tree research SPEC 2017 benchmarks",  # name
        "gem5/build/X86/gem5.fast",  # gem5_binary
        "configs/run_spec.py",  # run_script
        # relative_outdir
        f"out/spec/{bench}/{repl}/{assoc}",
        gem5_binary,  # gem5_artifact
        gem5_repo,  # gem5_git_artifact
        run_script_repo,  # run_script_git_artifact
        "./vmlinux-4.19.83",  # linux_binary
        "bench/spec-2017/spec2017-image/spec2017",  # disk_image
        linux_binary,  # linux_binary_artifact
        disk_image,  # disk_image_artifact
        ########
        # params
        ########
        "timing",
        # cpu,
        bench,
        "ref",
        # size,
        repl,
        str(assoc),
        ########
        # end params
        ########
        "-z",
        timeout=10 * 24 * 60 * 60,  # 10 days
    )


def work_run(run):
    run.run()
    json = run.dumpsJson()
    with open("out/spec/log.json", "a") as file:
        file.write(str(json))
    # print(json)


if __name__ == "__main__":
    cpus = ["kvm", "atomic", "o3", "timing"]
    benchmark_sizes = {
        "kvm": ["ref"]
        # "kvm": ["test", "ref"],
        # "atomic": ["test"],
        # "o3": ["test"],
        # "timing": ["test"],
    }
    benchmarks = [
        # "503.bwaves_r",
        # "507.cactuBSSN_r",
        # "508.namd_r",
        # "510.parest_r",
        # "511.povray_r",
        # "519.lbm_r",
        # "521.wrf_r",
        # "526.blender_r",
        # "527.cam4_r",
        # "538.imagick_r",
        # "544.nab_r",
        # "549.fotonik3d_r",
        # "554.roms_r",
        # "997.specrand_fr",
        "603.bwaves_s",
        "607.cactuBSSN_s",
        "619.lbm_s",
        "621.wrf_s",
        "627.cam4_s",
        "628.pop2_s",
        "638.imagick_s",
        "644.nab_s",
        "649.fotonik3d_s",
        "654.roms_s",
        # "996.specrand_fs",
        # "500.perlbench_r",
        # "502.gcc_r",
        # "505.mcf_r",
        # "520.omnetpp_r",
        # "523.xalancbmk_r",
        # "525.x264_r",
        # "531.deepsjeng_r",
        # "541.leela_r",
        # "548.exchange2_r",
        # "557.xz_r",
        # "999.specrand_ir",
        "600.perlbench_s",
        "602.gcc_s",
        "605.mcf_s",
        "620.omnetpp_s",
        "623.xalancbmk_s",
        "625.x264_s",
        "631.deepsjeng_s",
        "641.leela_s",
        "648.exchange2_s",
        "657.xz_s",
        # "998.specrand_is",
    ]

    repls = [
        "s",  # SIEVE
        *[  # 3Tree
            "3" + cold + hot + choice
            for cold in ["r", "l", "f"]
            for hot in ["r", "l", "f"]
            for choice in ["h", "q", "e", "n"]
        ],
        "t",  # TreePLRU
        # "2",  # 2Q (defunct)
        "?",  # Random
    ]

    assocs = [16, 8, 4]

    jobs = []
    runs = starmap(
        create_run,
        product(benchmarks, repls, assocs),
    )
    for run in runs:
        jobs.append(run)

    with mp.Pool(mp.cpu_count() - 6) as pool:
        pool.map(work_run, jobs)
    # for cpu in cpus:
    #     for size in benchmark_sizes[cpu]:
    #         for benchmark in benchmarks:
    #             run = create_run(benchmark, "uh", "assoc")
    #             runs.append(run)

    # run_job_pool(runs)
