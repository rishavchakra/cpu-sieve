from itertools import starmap, product
from gem5art.artifact import Artifact
from gem5art.run import gem5Run
import multiprocessing as mp

parsec_repo = Artifact.registerArtifact(
    command="""mkdir parsec-benchmark/;
    cd parsec-benchmark;
    git clone https://github.com/cirosantilli/parsec-benchmark.git""",
    typ="git repo",
    name="parsec_repo",
    path="./bench/parsec/parsec-benchmark/",
    cwd="./disk-image/",
    documentation="main repo to copy parsec source to the disk-image",
)

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
        scons defconfig gem5_build build_opts/X86
        scons setconfig gem5_build USE_KVM=y
        scons gem5_build/X86/gem5.fast -j24
    """,
    typ="git repo",
    name="gem5",
    path="gem5/",
    cwd="./",
    documentation="cloned gem5 at sieve-research branch",
)

gem5_binary = Artifact.registerArtifact(
    command="scons gem5_build/X86/gem5.fast -j24",
    typ="gem5 binary",
    name="gem5-20.1.0.4",
    cwd="gem5/",
    path="gem5/gem5_build/X86/gem5.fast",
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
    command="./packer build parsec/parsec.json",
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
    path="bench/configs",
    cwd="./",
    documentation="gem5 run scripts made specifically for SPEC benchmarks",
)


def create_run(bench, repl, assoc):
    return gem5Run.createFSRun(
        "3Tree research PARSEC benchmarks",  # name
        "gem5/gem5_build/X86/gem5.fast",
        "configs/run_spec.py",
        f"out/spec/{bench}/{repl}/{assoc}",
        gem5_binary,
        gem5_repo,
        run_script_repo,
        "./vmlinux-4.19.83",
        "bench/parsec/parsec-image/parsec",
        linux_binary,
        disk_image,
        ########
        # params
        ########
        # cpu
        "timing",
        bench,
        # benchmark size
        "simsmall",
        1,
        timeout=24 * 60 * 60,
    )


def work_run(run):
    run.run()
    json = run.dumpsJson()
    with open("out/parsec/log.json", "a") as file:
        file.write(str(json))


if __name__ == "__main__":
    benchmarks = [
        "blackscholes",
        "bodytrack",
        "canneal",
        "dedup",
        "facesim",
        "ferret",
        "fluidanimate",
        "freqmine",
        "raytrace",
        "streamcluster",
        "swaptions",
        "vips",
        "x264",
    ]
    repls = [
        "s",  # SIEVE
        *[  # 2Tree
            "2" + cold + hot + choice
            for cold in ["r", "l", "f"]
            for hot in ["r", "l", "f"]
            for choice in ["h", "q", "e", "n"]
        ],
        "3",  # 3Tree
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
