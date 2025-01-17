import os
import sys
from uuid import UUID

from gem5art.artifact import Artifact
from gem5art.run import gem5Run
from gem5art.tasks.tasks import run_gem5_instance
from gem5art.tasks.tasks import run_job_pool

spec_image_repo = Artifact.registerArtifact(
    # This line may go after `cd gem5-resources`
    # git checkout 1fe56ffc94005b7fa0ae5634c6edc5e2cb0b7357
    command="""
        git clone https://github.com/gem5/gem5-resources
        cd gem5-resources
        cd src/spec-2017
        git init
        git remote add origin https://github.com/rishavchakra/spec-cpu-tests.git
    """,
    typ="git repo",
    name="spec2017 Experiment",
    path="./",
    cwd="./",
    documentation="""
        local repo to run spec 2017 experiments with gem5 full system mode;
        resources cloned from https://github.com/gem5/gem5-resources upto commit 1fe56ffc94005b7fa0ae5634c6edc5e2cb0b7357 of stable branch
    """,
)

gem5_repo = Artifact.registerArtifact(
    command="""
            git clone -b sieve-research https://github.com/rishavchakra/gem5;
            cd gem5;
        """,
    typ="git repo",
    name="gem5",
    path="../gem5/",
    cwd="./",
    documentation="cloned gem5 rishav branch from github",
)

gem5_binary = Artifact.registerArtifact(
    command="scons build/X86/gem5.opt -j8",
    typ="gem5 binary",
    name="gem5",
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
    command="""wget https://releases.hashicorp.com/packer/1.4.3/packer_1.4.3_linux_amd64.zip;
    unzip packer_1.4.3_linux_amd64.zip;
    """,
    typ="binary",
    name="packer",
    path="disk-image/packer",
    cwd="disk-image",
    documentation="Program to build disk images. Downloaded sometime in August from hashicorp.",
)

disk_image = Artifact.registerArtifact(
    command="./packer build spec-2017/spec-2017.json",
    typ="disk image",
    name="spec-2017",
    cwd="disk-image/",
    path="disk-image/spec-2017/spec-2017-image/spec-2017",
    inputs=[
        packer,
        spec_image_repo,
        m5_binary,
    ],
    documentation="Ubuntu Server with SPEC 2017 installed, m5 binary installed and root auto login",
)

linux_repo = Artifact.registerArtifact(
    command="""git clone --branch v4.19.83 --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git;
    mv linux linux-stable""",
    typ="git repo",
    name="linux-stable",
    path="linux-stable/",
    cwd="./",
    documentation="linux kernel source code repo",
)

linux_binary = Artifact.registerArtifact(
    name="vmlinux-4.19.83",
    typ="kernel",
    path="linux-stable/vmlinux-4.19.83",
    cwd="linux-stable/",
    command="""
    cp ../config.4.19.83 .config;
    make -j8;
    cp vmlinux vmlinux-4.19.83;
    """,
    inputs=[
        spec_image_repo,
        linux_repo,
    ],
    documentation="kernel binary for v4.19.83",
)

run_script_repo = Artifact.registerArtifact(
    # This line may go after `cd gem5-resources`
    # git checkout 1fe56ffc94005b7fa0ae5634c6edc5e2cb0b7357
    command="""
        git clone https://github.com/rishavchakra/spec-run-scripts.git
    """,
    typ="git repo",
    name="spec2017 Experiment",
    path="run_scripts/spec",
    cwd="run_scripts/spec",
    documentation="""
        local repo of gem5 FS run scripts
    """,
)

if __name__ == "__main__":
    # cpus = ["kvm", "atomic", "o3", "timing"]
    cpus = ["kvm"]
    benchmark_sizes = {
        "kvm": ["test", "ref"],
        "atomic": ["test"],
        "o3": ["test"],
        "timing": ["test"],
    }
    # test: verifying that workloads get the right answers (not a problem for this research)
    # train: same as test? documentation confusing
    # ref: run the workloads
    size = "ref"
    # 5XX: SPECrate (throughput, generally smaller)
    # 6XX: SPECspeed (speed, generally larger/heavier)
    # 6XX benchmarks (and speed specrand benchmarks) are disabled
    benchmarks = [
        "503.bwaves_r",
        "507.cactuBSSN_r",
        "508.namd_r",
        "510.parest_r",
        "511.povray_r",
        "519.lbm_r",
        "521.wrf_r",
        "526.blender_r",
        "527.cam4_r",
        "538.imagick_r",
        "544.nab_r",
        "549.fotonik3d_r",
        "554.roms_r",
        "997.specrand_fr",
        # "603.bwaves_s",
        # "607.cactuBSSN_s",
        # "619.lbm_s",
        # "621.wrf_s",
        # "627.cam4_s",
        # "628.pop2_s",
        # "638.imagick_s",
        # "644.nab_s",
        # "649.fotonik3d_s",
        # "654.roms_s",
        # "996.specrand_fs",
        "500.perlbench_r",
        "502.gcc_r",
        "505.mcf_r",
        "520.omnetpp_r",
        "523.xalancbmk_r",
        "525.x264_r",
        "531.deepsjeng_r",
        "541.leela_r",
        "548.exchange2_r",
        "557.xz_r",
        "999.specrand_ir",
        # "600.perlbench_s",
        # "602.gcc_s",
        # "605.mcf_s",
        # "620.omnetpp_s",
        # "623.xalancbmk_s",
        # "625.x264_s",
        # "631.deepsjeng_s",
        # "641.leela_s",
        # "648.exchange2_s",
        # "657.xz_s",
        # "998.specrand_is",
    ]
    assocs = [8, 16, 4, 2, 32]
    replacement_policies = [
        "sieve",
        # "tree-sieve",
        # "lru",
        # "fifo",
        "rr",
        # "second-chance",
        "tree-plru",
        # "weighted-lru",
        # "nru",
        # "rrip",
        # "2q",
    ]

    runs = []
    for cpu in cpus:
        for assoc in assocs:
            for benchmark in benchmarks:
                for repl in replacement_policies:
                    run = gem5Run.createFSRun(
                        "gem5 v20.1.0.4 spec 2017 experiment",  # name
                        "gem5/build/X86/gem5.opt",  # gem5_binary
                        "gem5-configs/run_spec.py",  # run_script
                        # relative_outdir
                        f"out/spec/{benchmark}/{repl}_{assoc}",
                        gem5_binary,  # gem5_artifact
                        gem5_repo,  # gem5_git_artifact
                        run_script_repo,  # run_script_git_artifact
                        "linux-4.19.83/vmlinux-4.19.83",  # linux_binary
                        "disk-image/spec2017/spec2017-image/spec2017",  # disk_image
                        linux_binary,  # linux_binary_artifact
                        disk_image,  # disk_image_artifact
                        # script params
                        cpu,
                        benchmark,
                        size,
                        assoc,
                        repl,
                        timeout=10 * 24 * 60 * 60,  # 10 days
                    )
                    runs.append(run)

    run_job_pool(runs)
