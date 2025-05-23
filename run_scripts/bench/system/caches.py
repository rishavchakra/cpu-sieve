# -*- coding: utf-8 -*-
# Copyright (c) 2016 Jason Lowe-Power
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
#
# Authors: Jason Lowe-Power

""" Caches with options for a simple gem5 configuration script

This file contains L1 I/D and L2 caches to be used in the simple
gem5 configuration script.
"""

import m5
from m5.objects import *
from m5.params import AddrRange, AllMemory, MemorySize
from m5.util.convert import toMemorySize

# Some specific options for caches
# For all options see src/mem/cache/BaseCache.py


class L1Cache(Cache):
    """Simple L1 Cache with default values"""

    assoc = 8
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 16
    tgts_per_mshr = 20
    writeback_clean = True

    def __init__(self):
        super(L1Cache, self).__init__()
        pass

    def connectBus(self, bus):
        """Connect this cache to a memory-side bus"""
        self.mem_side = bus.slave

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU-side port
        This must be defined in a subclass"""
        raise NotImplementedError


class L1ICache(L1Cache):
    """Simple L1 instruction cache with default values"""

    # Set the default size
    size = "32kB"

    def __init__(self):
        super(L1ICache, self).__init__()

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU icache port"""
        self.cpu_side = cpu.icache_port


class L1DCache(L1Cache):
    """Simple L1 data cache with default values"""

    # Set the default size
    size = "32kB"

    def __init__(self):
        super(L1DCache, self).__init__()

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU dcache port"""
        self.cpu_side = cpu.dcache_port


class MMUCache(Cache):
    # Default parameters
    size = "8kB"
    assoc = 4
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 20
    tgts_per_mshr = 12
    writeback_clean = True

    def __init__(self):
        super(MMUCache, self).__init__()

    def connectCPU(self, cpu):
        """Connect the CPU itb and dtb to the cache
        Note: This creates a new crossbar
        """
        self.mmubus = L2XBar()
        self.cpu_side = self.mmubus.master
        for tlb in [cpu.itb, cpu.dtb]:
            self.mmubus.slave = tlb.walker.port

    def connectBus(self, bus):
        """Connect this cache to a memory-side bus"""
        self.mem_side = bus.slave


class L2Cache(Cache):
    """Simple L2 Cache with default values"""

    # Default parameters
    size = "256kB"
    assoc = 16
    tag_latency = 10
    data_latency = 10
    response_latency = 1
    mshrs = 20
    tgts_per_mshr = 12
    writeback_clean = True

    def __init__(self):
        super(L2Cache, self).__init__()

    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.master

    def connectMemSideBus(self, bus):
        self.mem_side = bus.slave


class L3Cache(Cache):
    """Simple L3 Cache bank with default values
    This assumes that the L3 is made up of multiple banks. This cannot
    be used as a standalone L3 cache.
    """

    # Default parameters
    assoc = 32
    tag_latency = 40
    data_latency = 40
    response_latency = 10
    mshrs = 256
    tgts_per_mshr = 12
    clusivity = "mostly_excl"

    size = "4MB"

    def __init__(self):
        super(L3Cache, self).__init__()

    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.master

    def connectMemSideBus(self, bus):
        self.mem_side = bus.slave


"""
----------------------------------------------------------------
Eviction set-specific caches
----------------------------------------------------------------
"""

"""
SIEVE caches
"""


class L1I_SIEVE(L1ICache):
    replacement_policy = SIEVERP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L1D_SIEVE(L1DCache):
    replacement_policy = SIEVERP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L2_SIEVE(L2Cache):
    replacement_policy = SIEVERP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


"""
Random Replacement caches
"""


class L1I_RR(L1ICache):
    replacement_policy = RandomRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L1D_RR(L1DCache):
    replacement_policy = RandomRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L2_RR(L2Cache):
    replacement_policy = RandomRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


"""
FIFO caches
"""


class L1I_FIFO(L1ICache):
    replacement_policy = FIFORP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L1D_FIFO(L1DCache):
    replacement_policy = FIFORP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L2_FIFO(L2Cache):
    replacement_policy = FIFORP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


"""
LRU caches
"""


class L1I_LRU(L1ICache):
    replacement_policy = LRURP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L1D_LRU(L1DCache):
    replacement_policy = LRURP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L2_LRU(L2Cache):
    replacement_policy = LRURP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


"""
Second Chance caches
"""


class L1I_SecondChance(L1ICache):
    replacement_policy = SecondChanceRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L1D_SecondChance(L1DCache):
    replacement_policy = SecondChanceRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L2_SecondChance(L2Cache):
    replacement_policy = SecondChanceRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


"""
Tree PLRU caches
"""


class L1I_TreePLRU(L1ICache):
    replacement_policy = TreePLRURP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L1D_TreePLRU(L1DCache):
    replacement_policy = TreePLRURP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L2_TreePLRU(L2Cache):
    replacement_policy = TreePLRURP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


"""
RRIP caches
"""


class L1I_RRIP(L1ICache):
    replacement_policy = RRIPRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L1D_RRIP(L1DCache):
    replacement_policy = RRIPRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L2_RRIP(L2Cache):
    replacement_policy = RRIPRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


"""
BRRIP caches
"""


class L1I_BRRIP(L1ICache):
    replacement_policy = BRRIPRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L1D_BRRIP(L1DCache):
    replacement_policy = BRRIPRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L2_BRRIP(L2Cache):
    replacement_policy = BRRIPRP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


"""
NRU caches
"""


class L1I_NRU(L1ICache):
    replacement_policy = NRURP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L1D_NRU(L1DCache):
    replacement_policy = NRURP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc


class L2_NRU(L2Cache):
    replacement_policy = NRURP()

    def __init__(self, assoc):
        super().__init__()
        self.assoc = assoc
