#!/usr/bin/python
# -*- coding: utf-8 -*-
from gurobipy import *

sas = 'SAS'
sata = 'SATA'
hdd = 'HDD'
ssd = 'SSD'
nvme = 'NVME'
ddr4 = 'DDR4'
ddr3 = 'DDR3'
dom = 'DOM'  # disk on module
domssd = dom + ssd
rj45 = "RJ45"
qsfp = "QSFP"
qsfpplus = "QSFP+"
qsfp28 = "QSFP28"
sfp28 = "SFP28"
sfp = "SFP"
sfpplus = "SFP+"
intel = "Intel"
mellanox = "Mellanox"
supermicro = "Super Micro"


class Cpu:

    def __init__(self, model, cores, ghz, cost, name, cachemb=0, watts=0, family='xeon', minCount=0):
        self.cores = cores
        self.ghz = ghz
        self.cost = cost
        self.name = name
        self.cacheMB = cachemb
        self.watts = watts
        self.family = family
        baseVarName = "cpu {} {} @{}".format(family, cores, ghz)
        self.countVar = model.addVar(lb=0, vtype=GRB.INTEGER, name=baseVarName)
        self.useVar = model.addVar(vtype=GRB.BINARY, name="use " + baseVarName)
        model.addConstr(self.countVar - 10000 * self.useVar, GRB.LESS_EQUAL, 0, "distinctCpus " + baseVarName)


class Memory:

    def __init__(self, model, gb, memoryType, mhz, cost, ddr='DDR4'):
        self.memoryGB = gb
        self.type = memoryType
        self.MHz = mhz
        self.cost = cost
        self.ddrType = ddr
        baseVarName = "memory {}GB {}".format(self.memoryGB, self.type)
        self.countVar = model.addVar(lb=0, vtype=GRB.INTEGER, name=baseVarName)
        self.useVar = model.addVar(vtype=GRB.BINARY, name="use " + baseVarName)
        model.addConstr(self.countVar - 10000 * self.useVar, GRB.LESS_EQUAL, 0, "distinctMemory " + baseVarName)


class Disk:

    def __init__(self, model, tb, size, cost, iops, protocol, gbps, partnumber, disktype=hdd, streammbs=0):
        self.tb = tb
        self.iops = iops
        # Simplified generalizations
        if streammbs == 0:
            if disktype == hdd:
                self.streamMBs = 200
            if disktype == ssd:
                self.streamMBs = 600
            if disktype == nvme:
                self.streamMBs = 1500
        else:
            self.streamMBs = streammbs
        self.type = disktype
        self.size = size
        self.protocol = protocol
        self.gbps = gbps
        self.partNumber = partnumber
        self.cost = cost
        baseVarName = "disk {}TB {}\" {} {}".format(self.tb, self.size, self.protocol, self.partNumber)
        self.countVar = model.addVar(lb=0, vtype=GRB.INTEGER, name=baseVarName)
        self.useVar = model.addVar(vtype=GRB.BINARY, name="use " + baseVarName)
        model.addConstr(self.countVar - 10000 * self.useVar, GRB.LESS_EQUAL, 0, "distinctDisks " + baseVarName)


class Network:

    def __init__(self, model, cost, speed, adapterType, adapterCount, manufacturer):
        self.cost = cost
        self.speedGbit = speed
        self.adapterType = adapterType
        self.adapterCount = adapterCount
        self.manufacturer = manufacturer
        baseVarName = "network {} x {} @ {} Gigabit by {}".format(adapterCount, adapterType, speed, manufacturer)
        self.countVar = model.addVar(lb=0, vtype=GRB.INTEGER, name=baseVarName)
        self.useVar = model.addVar(vtype=GRB.BINARY, name="use " + baseVarName)
        model.addConstr(self.countVar - 10000 * self.useVar, GRB.LESS_EQUAL, 0, "distinctNetworkCards " + baseVarName)


class Server:

    def __init__(self, model, name, url, cost, watts, rackunits, cpuslots, memoryslots, minmemoryslots, disk25slots, disk35slots, nvmeslots, minimum25disks, minimum35disks, osdisks, osdisktype, x16, x8, onboardnetworkports, siomcards, powersupplies, nodes):
        self.name = name
        self.url = url
        self.cost = cost
        self.watts = watts
        self.rackUnits = rackunits
        self.cpuSlots = cpuslots
        self.memorySlots = memoryslots
        self.minMemorySlots = minmemoryslots
        self.disk25Slots = disk25slots
        self.disk35Slots = disk35slots
        self.nvmeSlots = nvmeslots
        self.minimum25Disks = minimum25disks
        self.minimum35Disks = minimum35disks
        self.osDisks = osdisks
        self.osDiskType = osdisktype
        self.pcieV3X16Slots = x16
        self.pcieV3X8Slots = x8
        self.onBoardNetworkPorts = onboardnetworkports
        self.siomCards = siomcards
        self.powerSupplies = powersupplies
        self.nodes = nodes

        supportCost = 450
        self.configuredCost = cost + 139 * osdisks + supportCost
        baseVarName = "server " + self.name
        self.countVar = model.addVar(lb=0, vtype=GRB.INTEGER, name=baseVarName)
        self.useVar = model.addVar(vtype=GRB.BINARY, name="use " + baseVarName)
        model.addConstr(self.countVar - 10000 * self.useVar, GRB.LESS_EQUAL, 0, "distinctServers " + baseVarName)

    def __str__(self):
        return self.name + ":" + str(self.configuredCost)


class Rack:
    availableRackUnits = 0
    availableWatts = 0
    networkCost = 0
    costPerMonth = 0
    timeHorizonYears = 0
    useVar = None
    rackUnits = LinExpr()
    watts = LinExpr()

    def __init__(self, model, name, availableRackUnits, availableWatts, networkCost, costPerMonth, timeHorizonYears):
        self.availableRackUnits = availableRackUnits
        self.availableWatts = availableWatts
        self.networkCost = networkCost
        self.costPerMonth = costPerMonth
        self.timeHorizonYears = timeHorizonYears
        self.useVar = model.addVar(vtype=GRB.BINARY, name="rack " + name)


def buildVars(m):
    cpus = [Cpu(m, 6, 1.7, 249, 'E5 - 2603', 15, 85),
            Cpu(m, 8, 1.7, 369, 'E5 - 2609', 20, 85),
            Cpu(m, 8, 2.1, 499, 'E5 - 2620', 20, 85),
            Cpu(m, 10, 2.2, 769, 'E5 - 2630', 25, 85),
            Cpu(m, 10, 2.4, 1079, 'E5 - 2640', 25, 90),
            Cpu(m, 12, 2.2, 1299, 'E5 - 2650', 30, 105),
            Cpu(m, 14, 2, 1599, 'E5 - 2660', 35, 105),
            Cpu(m, 14, 2.4, 1999, 'E5 - 2680', 35, 120),
            Cpu(m, 14, 2.6, 2349, 'E5 - 2690', 35, 135),
            Cpu(m, 10, 1.8, 729, 'E5 - 2630L', 25, 55),
            Cpu(m, 14, 1.7, 1499, 'E5 - 2650L', 35, 65),
            Cpu(m, 4, 2.6, 509, 'E5 - 2623', 10, 85),
            Cpu(m, 4, 3.5, 1149, 'E5 - 2637', 15, 135),
            Cpu(m, 6, 3.4, 1799, 'E5 - 2643', 20, 135),
            Cpu(m, 8, 3.2, 2349, 'E5 - 2667', 25, 135),
            Cpu(m, 16, 2.1, 1999, 'E5 - 2683', 40, 120),
            Cpu(m, 18, 2.1, 2699, 'E5 - 2695', 45, 120),
            Cpu(m, 16, 2.6, 3249, 'E5 - 2697A', 40, 145),
            Cpu(m, 18, 2.3, 2999, 'E5 - 2697', 45, 145),
            Cpu(m, 20, 2.2, 3599, 'E5 - 2698', 50, 135),
            Cpu(m, 22, 2.2, 4599, 'E5 - 2699', 55, 145),
            Cpu(m, 22, 2.4, 5499, 'E5 - 2699A', 55, 145)]

    memory = [#Memory(m, 4, 'Registered', 2400, 69),
              #Memory(m, 8, 'Registered', 2400, 139),
              Memory(m, 16, 'Registered', 2400, 229),
              Memory(m, 32, 'Registered', 2400, 399),
              Memory(m, 64, 'Registered', 2400, 929),
              Memory(m, 32, 'Load - Reduced', 2400, 479),
              Memory(m, 64, 'Load - Reduced', 2400, 999)]

    disk25 = [Disk(m, 5, 2.5, 213, 90, sata, 6, 'Barracuda5TB5400'),
              Disk(m, .3, 2.5, 189, 166, sas, 12, '0B28810'),
              Disk(m, .6, 2.5, 239, 166, sas, 12, '0B28808'),
              Disk(m, .9, 2.5, 309, 166, sas, 12, '0B27976'),
              Disk(m, 1.2, 2.5, 339, 166, sas, 12, '0B28807'),
              Disk(m, .3, 2.5, 269, 250, sas, 12, '0B28955'),
              Disk(m, .6, 2.5, 399, 250, sas, 12, '0B28953'),
              Disk(m, 1, 2.5, 209, 120, sata, 6, 'ST1000NX0313'),
              Disk(m, 2, 2.5, 349, 120, sata, 6, 'ST2000NX0253'),
              Disk(m, 1, 2.5, 229, 120, sas, 12, 'ST1000NX0333'),
              Disk(m, 2, 2.5, 389, 120, sas, 12, 'ST2000NX0273'),
              Disk(m, .6, 2.5, 189, 166, sas, 12, 'ST600MM0018'),
              Disk(m, .9, 2.5, 299, 166, sas, 12, 'ST900MM0018'),
              Disk(m, 1.2, 2.5, 339, 166, sas, 12, 'ST1200MM0018'),
              Disk(m, 1.8, 2.5, 439, 166, sas, 12, 'ST1800MM0018'),
              Disk(m, .3, 2.5, 249, 250, sas, 12, 'ST300MP0005'),
              Disk(m, .6, 2.5, 359, 250, sas, 12, 'ST600MP0005'),
              Disk(m, .24, 2.5, 149, 5000, sata, 6, 'Intel DC S4500 240', ssd),
              Disk(m, .48, 2.5, 259, 5000, sata, 6, 'Intel DC S4500 480', ssd),
              Disk(m, .96, 2.5, 489, 5000, sata, 6, 'Intel DC S4500 960', ssd),
              Disk(m, 1.92, 2.5, 979, 5000, sata, 6, 'Intel DC S4500 1920', ssd),
              Disk(m, 3.84, 2.5, 1999, 5000, sata, 6, 'Intel DC S4500 3840', ssd),
              Disk(m, .24, 2.5, 199, 5000, sata, 6, 'Intel DC S4600 240', ssd),
              Disk(m, .48, 2.5, 329, 5000, sata, 6, 'Intel DC S4600 480', ssd),
              Disk(m, .96, 2.5, 629, 5000, sata, 6, 'Intel DC S4600 960', ssd),
              Disk(m, 1.92, 2.5, 1259, 5000, sata, 6, 'Intel DC S4600 1920', ssd),
              Disk(m, .48, 2.5, 279, 5000, sata, 6, 'Micron M5100 ECO 480', ssd),
              Disk(m, 0.96, 2.5, 489, 5000, sata, 6, 'Micron M5100 ECO 960', ssd),
              Disk(m, 1.92, 2.5, 769, 5000, sata, 6, 'Micron M5100 ECO 1920', ssd),
              Disk(m, 3.84, 2.5, 1459, 5000, sata, 6, 'Micron M5100 ECO 3840', ssd),
              Disk(m, 7.68, 2.5, 2959, 5000, sata, 6, 'Micron M5100 ECO 7680', ssd),
              Disk(m, 0.24, 2.5, 159, 5000, sata, 6, 'Micron M5100 PRO 240', ssd),
              Disk(m, .48, 2.5, 289, 5000, sata, 6, 'Micron M5100 PRO 480', ssd),
              Disk(m, 0.96, 2.5, 499, 5000, sata, 6, 'Micron M5100 PRO 960', ssd),
              Disk(m, 1.92, 2.5, 899, 5000, sata, 6, 'Micron M5100 PRO 1920', ssd),
              Disk(m, 3.84, 2.5, 1719, 5000, sata, 6, 'Micron M5100 PRO 3840', ssd),
              Disk(m, 0.24, 2.5, 199, 5000, sata, 6, 'Micron M5100 MAX 240', ssd),
              Disk(m, .48, 2.5, 339, 5000, sata, 6, 'Micron M5100 MAX 480', ssd),
              Disk(m, 0.96, 2.5, 619, 5000, sata, 6, 'Micron M5100 MAX 960', ssd),
              Disk(m, 1.92, 2.5, 1179, 5000, sata, 6, 'Micron M5100 MAX 1920', ssd),
             ]

    disk35 = [Disk(m, 2, 3.5, 149, 120, sata, 6, '0F23092'),
              Disk(m, 4, 3.5, 199, 120, sata, 6, '0F23090'),
              Disk(m, 6, 3.5, 239, 120, sata, 6, '0F23001'),
              Disk(m, 8, 3.5, 339, 120, sata, 6, '0F23267'),
              Disk(m, 10, 3.5, 399, 120, sata, 6, '0F27604'),
              Disk(m, 12, 3.5, 589, 120, sata, 6, '0F30144'),
              Disk(m, 2, 3.5, 179, 120, sas, 12, '0F22799'),
              Disk(m, 4, 3.5, 219, 120, sas, 12, '0F22795'),
              Disk(m, 6, 3.5, 259, 120, sas, 12, '0F22791'),
              Disk(m, 8, 3.5, 369, 120, sas, 12, '0F23268'),
              Disk(m, 10, 3.5, 429, 120, sas, 12, '0F27352'),
              Disk(m, 12, 3.5, 609, 120, sas, 12, '0F27352'),
              Disk(m, 1, 3.5, 119, 120, sata, 6, 'ST1000NM0055'),
              Disk(m, 2, 3.5, 139, 120, sata, 6, 'ST2000NM0055'),
              Disk(m, 4, 3.5, 209, 120, sata, 6, 'ST4000NM0035'),
              Disk(m, 6, 3.5, 269, 120, sata, 6, 'ST6000NM0115'),
              Disk(m, 8, 3.5, 339, 120, sata, 6, 'ST8000NM0055'),
              Disk(m, 10, 3.5, 439, 120, sata, 6, 'ST10000NM0086'),
              Disk(m, 12, 3.5, 569, 120, sata, 6, 'ST12000NM0007'),
              Disk(m, 1, 3.5, 139, 120, sas, 12, 'ST1000NM0045'),
              Disk(m, 2, 3.5, 169, 120, sas, 12, 'ST2000NM0045'),
              Disk(m, 4, 3.5, 219, 120, sas, 12, 'ST4000NM0025'),
              Disk(m, 6, 3.5, 259, 120, sas, 12, 'ST6000NM0095'),
              Disk(m, 8, 3.5, 329, 120, sas, 12, 'ST8000NM0075'),
              Disk(m, 10, 3.5, 449, 120, sas, 12, 'ST10000NM0096'),
              Disk(m, 12, 3.5, 529, 120, sas, 12, 'ST12000NM0027'),
              Disk(m, 1, 3.5, 209, 120, sata, 6, 'ST1000NX0313'),
              Disk(m, 2, 3.5, 349, 120, sata, 6, 'ST2000NX0253'),
             ]

    diskNvme = [Disk(m, 2, 1.5, 1149, 20000, nvme, 24, 'Intel P3520 NVMe', nvme),
            Disk(m, 4, 1.5, 2799, 20000, nvme, 24, 'Intel P4500 NVMe', nvme),
            Disk(m, 2, 1.5, 1952, 20000, nvme, 24, 'Intel P4600 NVMe 2TB', nvme),
            Disk(m, 4, 1.5, 3590, 20000, nvme, 24, 'Intel P4600 NVMe 4TB', nvme),
            Disk(m, .375, 1.5, 1851, 20000, nvme, 24, 'Intel P4800X 375', nvme),
            Disk(m, .75, 1.5, 3653, 20000, nvme, 24, 'Intel P4800X 750', nvme)]

    siom = [Network(m, 62, 1, rj45, 2, supermicro),
            Network(m, 100, 1, rj45, 4, supermicro),
            Network(m, 188, 10, sfpplus, 2, supermicro),
            Network(m, 289, 10, sfpplus, 4, supermicro),
            Network(m, 201, 10, rj45, 2, supermicro),
            Network(m, 352, 10, rj45, 4, supermicro),
            Network(m, 327, 25, sfp28, 2, supermicro),
            Network(m, 770, 56, qsfp, 1, supermicro),
            Network(m, 1007, 56, qsfp, 2, supermicro)]

    pciNetwork = [# Network(m, 156, 1, rj45, 2, intel),
                  # Network(m, 365, 1, rj45, 4, intel),
                  # Network(m, 377, 10, sfpplus, 2, intel),
                  # Network(m, 478, 10, "LC", 1, intel),
                  # Network(m, 577, 10, "LC", 2, intel),
                  # Network(m, 415, 10, rj45, 1, intel),
                  # Network(m, 629, 10, rj45, 2, intel),
                  # Network(m, 365, 10, rj45, 1, intel),
                  # Network(m, 428, 10, rj45, 2, intel),
                  # Network(m, 365, 10, sfpplus, 2, intel),
                  # Network(m, 491, 10, sfpplus, 4, intel),
                  # Network(m, 743, 10, rj45, 4, intel),
                  # Network(m, 478, 40, qsfpplus, 1, intel),
                  # Network(m, 528, 40, qsfpplus, 2, intel),
                  # Network(m, 226, 10, sfpplus, 1, mellanox),
                  # Network(m, 289, 10, sfpplus, 2, mellanox),
                  # Network(m, 453, 56, qsfp, 1, mellanox),
                  # Network(m, 566, 56, qsfp, 2, mellanox),
                  # Network(m, 226, 10, sfp28, 1, mellanox),
                  # Network(m, 289, 10, sfp28, 2, mellanox),
                  # Network(m, 276, 25, sfp28, 1, mellanox),
                  # Network(m, 352, 25, sfp28, 2, mellanox),
                  # Network(m, 440, 40, qsfp28, 1, mellanox),
                  # Network(m, 503, 50, qsfp28, 1, mellanox),
                  # Network(m, 453, 56, qsfp28, 1, mellanox),
                  # Network(m, 566, 56, qsfp28, 2, mellanox),
                  # Network(m, 503, 50, qsfp28, 1, mellanox),
                  Network(m, 617, 50, qsfp28, 2, mellanox),
                  # Network(m, 843, 100, qsfp28, 1, mellanox),
                  Network(m, 1007, 100, qsfp28, 2, mellanox),
                  # Ignoring last 4 inifiniband network cards
                  ]

    servers = [
               Server(m, "24x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6028r-e1cr24n", 3705, 1600, 2, 2, 24, 8, 0, 24, 0, 0, 12, 2, domssd, 2, 1, 0, 1, 2, 1),
               Server(m, "16x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6028r-e1cr16t", 2391, 1000, 2, 2, 16, 8, 0, 16, 0, 0, 0, 2, domssd, 1, 6, 2, 0, 2, 1),
               #Server(m, "16x3.5 3U", "https://www.thinkmate.com/product/supermicro/ssg-6038r-e1cr16h", 2437, 920, 3, 2, 16, 8, 0, 16, 0, 0, 0, 2, domssd, 1, 6, 2, 0, 2, 1),
               Server(m, "90x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6048r-e1cr90l", 8774, 1000, 4, 2, 8, 8, 0, 90, 0, 0, 45, 2, domssd, 0, 0, 4, 1, 2, 1),
               Server(m, "72x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6048r-e1cr72l", 8689, 2000, 4, 2, 16, 8, 0, 72, 0, 0, 36, 2, domssd, 1, 3, 2, 0, 2, 1),
               Server(m, "60x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6048r-e1cr60n", 5353, 2000, 4, 2, 24, 8, 0, 60, 6, 0, 30, 2, dom, 2, 1, 0, 1, 2, 1),
               #Server(m, "36x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6048r-e1cr36n", 3480, 1280, 4, 2, 24, 8, 0, 36, 0, 0, 0, 2, dom, 1, 6, 4, 0, 2, 1),
               #Server(m, "24x3.5 4U", "https://www.thinkmate.com/product/supermicro/ssg-6048r-e1cr24n", 2892, 920, 4, 2, 24, 8, 0, 24, 0, 0, 0, 2, domssd, 1, 3, 4, 0, 2, 1),
               #Server(m, "12x3.5", "https://www.thinkmate.com/product/supermicro/sys-6028r-tdwnr", 1623, 920, 2, 2, 16, 8, 0, 12, 0, 0, 0, 2, dom, 0, 4, 2, 0, 2, 1),
               Server(m, "48x2.5", "https://www.thinkmate.com/product/supermicro/ssg-2028r-e1cr48n", 4146, 1600, 2, 2, 24, 8, 48, 0, 0, 24, 0, 2, domssd, 2, 1, 2, 1, 2, 1),
               Server(m, "24x2.5", "https://www.thinkmate.com/product/supermicro/ssg-2028r-e1cr24h", 2441, 920, 2, 2, 16, 8, 24, 0, 0, 0, 0, 2, domssd, 1, 6, 2, 0, 2, 1),
               Server(m, "24x2.5 4 Node", "https://www.thinkmate.com/product/supermicro/sys-2028tp-hc1r-siom", 4685, 2000, 2, 2, 16, 8, 6, 0, 0, 1, 0, 1, dom, 1, 1, 0, 1, 2, 4),
               #Server(m, "8x2.5 2 Node", "https://www.thinkmate.com/product/supermicro/sys-1028tp-dc1tr", 2718, 1000, 1, 2, 16, 8, 4, 0, 0, 0, 0, 1, dom, 1, 0, 2, 0, 2, 2),
               Server(m, "24x2.5 2 Node", "https://www.thinkmate.com/product/supermicro/sys-2028tp-dc1tr", 2989, 1280, 2, 2, 16, 8, 12, 0, 0, 0, 0, 1, dom, 1, 1, 2, 0, 2, 2),
               #Server(m, "16x2.5 2 Node", "https://www.thinkmate.com/product/supermicro/sys-2028tp-dttr", 2632, 1280, 2, 2, 16, 8, 8, 0, 0, 0, 0, 1, dom, 1, 1, 2, 0, 2, 2),
               ]

    racks = [Rack(m, "1", 32, availableWattsPerRack, 35000, rackCostPerMonth, serverCostTimeHorizonYears),
             Rack(m, "2", 32, availableWattsPerRack, 35000, rackCostPerMonth, serverCostTimeHorizonYears),
             Rack(m, "3", 36, availableWattsPerRack, 20000, rackCostPerMonth, serverCostTimeHorizonYears),]

    return cpus, memory, disk25, disk35, diskNvme, siom, pciNetwork, servers, racks


def ilp():
    m = Model("ILP")
    cpus, memory, disk25, disk35, diskNvme, siom, pciNetwork, servers, racks = buildVars(m)

    cost = LinExpr()

    ##### Server #####
    serverCount = LinExpr()
    nodeCount = LinExpr()
    serverTypes = LinExpr()
    rackUnits = LinExpr()
    watts = LinExpr()
    serverCpuSlots = LinExpr()
    serverMemorySlots = LinExpr()
    serverMinMemorySlots = LinExpr()
    server25DiskSlots = LinExpr()
    server35DiskSlots = LinExpr()
    serverNvmeSlots = LinExpr()
    min25Disks = LinExpr()
    min35Disks = LinExpr()
    maxSiomCards = LinExpr()
    maxPciNetworkCards = LinExpr()
    for server in servers:
        serverCount = serverCount + server.countVar
        nodeCount = nodeCount + server.countVar * server.nodes
        serverTypes = serverTypes + server.useVar
        rackUnits = rackUnits + server.countVar * server.rackUnits
        watts = watts + server.countVar * server.watts
        cost = cost + server.countVar * server.configuredCost
        serverCpuSlots = serverCpuSlots + server.countVar * (server.cpuSlots * server.nodes)
        serverMemorySlots = serverMemorySlots + server.countVar * (server.memorySlots * server.nodes)
        serverMinMemorySlots = serverMinMemorySlots + server.countVar * (server.minMemorySlots * server.nodes)
        server25DiskSlots = server25DiskSlots + server.countVar * (server.disk25Slots * server.nodes)
        min25Disks = min25Disks + server.countVar * (server.minimum25Disks * server.nodes)
        server35DiskSlots = server35DiskSlots + server.countVar * (server.disk35Slots * server.nodes)
        min35Disks = min35Disks + server.countVar * (server.minimum35Disks * server.nodes)
        serverNvmeSlots = serverNvmeSlots + server.countVar * (server.nvmeSlots * server.nodes)
        maxSiomCards = maxSiomCards + server.countVar * (server.siomCards * server.nodes)
        maxPciNetworkCards = maxPciNetworkCards + server.countVar * ((server.pcieV3X16Slots + server.pcieV3X8Slots) * server.nodes)

    m.addConstr(serverCount, GRB.GREATER_EQUAL, minServers, "minServers")
    m.addConstr(serverCount, GRB.LESS_EQUAL, maxServers, "maxServers")
    m.addConstr(serverTypes, GRB.LESS_EQUAL, maxDistinctServerTypes, "maxDistinctServerTypes")

    ##### Racks #####

    maxRackUnits = LinExpr()
    maxWatts = LinExpr()
    previousRack = None
    for rack in racks:
        if previousRack != None:
            m.addConstr(rack.useVar, GRB.LESS_EQUAL, previousRack.useVar, "rack {} after rack {}".format(rack, previousRack))
        previousRack = rack
        maxRackUnits = maxRackUnits + rack.useVar * rack.availableRackUnits
        maxWatts = maxWatts + rack.useVar * rack.availableWatts
        cost = cost + rack.useVar * rackCostScalingFactor * (rack.networkCost + (rack.costPerMonth * 12 * rack.timeHorizonYears))

    m.addConstr(rackUnits, GRB.LESS_EQUAL, maxRackUnits, "maxRackUnits")
    m.addConstr(watts, GRB.LESS_EQUAL, maxWatts, "maxWatts")

    ##### CPU #####
    cpuTypes = LinExpr()
    cpuCount = LinExpr()
    cores = LinExpr()
    gigaflops = LinExpr()
    for cpu in cpus:
        cpuTypes = cpuTypes + cpu.useVar
        cpuCount = cpuCount + cpu.countVar
        cores = cores + cpu.countVar * cpu.cores
        cost = cost + cpu.countVar * cpu.cost
        gigaflops = gigaflops + cpu.countVar * (cpu.cores * cpu.ghz)

    m.addConstr(cpuTypes, GRB.LESS_EQUAL, maxDistinctCpus, "distinctCpus")
    m.addConstr(serverCpuSlots, GRB.EQUAL, cpuCount, "fillCpuSlots")
    m.addConstr(cores, GRB.GREATER_EQUAL, minCores, "minCores")
    m.addConstr(gigaflops, GRB.GREATER_EQUAL, minGigaflops, "minGigaflops")

    ##### Memory #####
    memoryTypes = LinExpr()
    memoryGB = LinExpr()
    memorySlots = LinExpr()
    for mem in memory:
        memoryTypes = memoryTypes + mem.useVar
        memoryGB = memoryGB + mem.countVar * mem.memoryGB
        memorySlots = memorySlots + mem.countVar
        cost = cost + mem.countVar * mem.cost

    m.addConstr(memoryTypes, GRB.LESS_EQUAL, maxDistinctMemory, "distinctMemoryTypes")
    m.addConstr(memoryGB, GRB.GREATER_EQUAL, minMemory, "minMemory")
    m.addConstr(memorySlots, GRB.LESS_EQUAL, serverMemorySlots, "maxMemorySlotsAvailable")
    m.addConstr(memorySlots, GRB.GREATER_EQUAL, serverMinMemorySlots, "minMemorySlotsRequiredByServers")
    m.addConstr(nodeCount * maxAvgMemoryPerNode - memoryGB, GRB.GREATER_EQUAL, 0, "maxAvgMemoryPerNode")
    m.addConstr(nodeCount * minAvgMemoryPerNode - memoryGB, GRB.LESS_EQUAL, 0, "minAvgMemoryPerNode")

    ##### Disk #####
    allDisks = []
    allDisks.extend(disk25)
    allDisks.extend(disk35)
    allDisks.extend(diskNvme)

    diskTypes = LinExpr()
    diskTypes25 = LinExpr()
    diskTypes35 = LinExpr()
    diskTypesNvme = LinExpr()
    diskTB = LinExpr()
    diskHddTB = LinExpr()
    diskFastTB = LinExpr()
    diskIOPS = LinExpr()
    diskHddIOPS = LinExpr()
    diskFastIOPS = LinExpr()
    diskStreamMBs = LinExpr()
    disk25Count = LinExpr()
    disk35Count = LinExpr()
    diskNvmeCount = LinExpr()

    for disk in disk25:
        disk25Count = disk25Count + disk.countVar
        diskTypes25 = diskTypes25 + disk.useVar
    for disk in disk35:
        disk35Count = disk35Count + disk.countVar
        diskTypes35 = diskTypes35 + disk.useVar
    for disk in diskNvme:
        diskNvmeCount = diskNvmeCount + disk.countVar
        diskTypesNvme = diskTypesNvme + disk.useVar

    for disk in allDisks:
        diskTypes = diskTypes + disk.useVar
        diskTB = diskTB + disk.countVar * disk.tb
        diskIOPS = diskIOPS + disk.countVar * disk.iops
        diskStreamMBs = diskStreamMBs + disk.countVar * disk.streamMBs
        cost = cost + disk.countVar * disk.cost
        if disk.type == hdd:
            diskHddTB = diskHddTB + disk.countVar * disk.tb
            diskHddIOPS = diskHddIOPS + disk.countVar * disk.iops
        else:
            diskFastTB = diskFastTB + disk.countVar * disk.tb
            diskFastIOPS = diskFastIOPS + disk.countVar * disk.iops

    m.addConstr(diskTypes, GRB.LESS_EQUAL, maxDistinctDisks, "distinctDiskTypes")
    m.addConstr(diskTypes25, GRB.LESS_EQUAL, maxDistinct25Disks, "maxDistinct25Disks")
    m.addConstr(diskTypes35, GRB.LESS_EQUAL, maxDistinct35Disks, "maxDistinct35Disks")
    m.addConstr(diskTypesNvme, GRB.LESS_EQUAL, maxDistinctNvmeDisks, "maxDistinctNvmeDisks")
    m.addConstr(diskTB, GRB.GREATER_EQUAL, minDiskTB, "minimumTerabytes")
    m.addConstr(diskHddTB, GRB.GREATER_EQUAL, minDiskHddTB, "minimumHddTB")
    m.addConstr(diskFastTB, GRB.GREATER_EQUAL, minDiskFastTB, "minimumFastTB")
    m.addConstr(diskIOPS, GRB.GREATER_EQUAL, minDiskIOPS, "minimumIOPS")
    m.addConstr(diskHddIOPS, GRB.GREATER_EQUAL, minDiskHddIOPS, "minimumHddIOPS")
    m.addConstr(diskFastIOPS, GRB.GREATER_EQUAL, minDiskFastIOPS, "minimumFastIOPS")
    m.addConstr(diskStreamMBs, GRB.GREATER_EQUAL, minDiskStreamMBs, "minimumStreamMBs")
    m.addConstr(disk25Count + disk35Count + diskNvmeCount, GRB.GREATER_EQUAL, minDiskCount, "minDiskCount")
    if fillAllDiskSlots:
        m.addConstr(disk35Count, GRB.EQUAL, server35DiskSlots, "fillAll35DiskSlots")
        m.addConstr(disk25Count, GRB.EQUAL, server25DiskSlots, "fillAll25DiskSlots")
    else:
        m.addConstr(disk35Count, GRB.GREATER_EQUAL, min35Disks, "min35DiskRequirement")
        m.addConstr(disk35Count, GRB.LESS_EQUAL, server35DiskSlots, "max35DiskSlots")
        m.addConstr(disk25Count, GRB.GREATER_EQUAL, min25Disks, "min25DiskRequirement")
        m.addConstr(disk25Count, GRB.LESS_EQUAL, server25DiskSlots, "max25DiskSlots")

    ##### Network #####
    networks = []
    networks.extend(siom)
    networks.extend(pciNetwork)

    networkSpeed = LinExpr()
    networkCards = LinExpr()
    networkConnections = LinExpr()
    networkTypes = LinExpr()
    for network in networks:
        networkSpeed = networkSpeed + network.countVar * (network.speedGbit * network.adapterCount)
        networkCards = networkCards + network.countVar
        networkConnections = networkConnections + network.countVar * network.adapterCount
        networkTypes = networkTypes + network.useVar
        cost = cost + network.countVar * network.cost

    siomCardCount = LinExpr()
    for s in siom:
        siomCardCount = siomCardCount + s.countVar

    pciNetworkCount = LinExpr()
    for pci in pciNetwork:
        pciNetworkCount = pciNetworkCount + pci.countVar

    m.addConstr(networkSpeed, GRB.GREATER_EQUAL, minTotalNetworkSpeedGigabits, "minTotalNetworkSpeed")
    m.addConstr(networkCards, GRB.GREATER_EQUAL, nodeCount * minNetworkCardsPerServer, "minNetworkCardPerNode")
    m.addConstr(networkCards, GRB.LESS_EQUAL, nodeCount * maxNetworkCardsPerServer, "maxNetworkCardsPerNode")
    m.addConstr(networkCards, GRB.LESS_EQUAL, maxNetworkConnections, "maxNetworkConnections")
    m.addConstr(networkConnections, GRB.GREATER_EQUAL, minNetworkConnectionsPerNode * nodeCount, "minNetworkConnections")
    m.addConstr(siomCardCount, GRB.LESS_EQUAL, maxSiomCards if allowSiomCards else 0, "maxSiomCards")
    m.addConstr(pciNetworkCount, GRB.LESS_EQUAL, maxPciNetworkCards, "maxPciNetworkCards")
    m.addConstr(networkTypes, GRB.LESS_EQUAL, maxDistinctNetworkCards, "maxDistinctNetworkCards")


    ##### Objective #####

    m.setObjective(cost, GRB.MINIMIZE)

    m.optimize()

    for v in m.getVars():
        if abs(v.X) > 1e-6 and not v.varName.startswith("use "):
            print (v.varName, int(round(v.X, 0)))
    return m.getAttr("ObjVal")


##### inputs #####

# Servers
maxDistinctServerTypes = 1
minServers = 0
maxServers = 50

# Memory
maxDistinctMemory = 1
minMemory = 10240
maxAvgMemoryPerNode = 3000
minAvgMemoryPerNode = 256

# Cpus
maxDistinctCpus = 1
minCores = 0
minGigaflops = 2300 + 700

# Disk
maxDistinctDisks = 3
maxDistinct25Disks = 1
maxDistinct35Disks = 1
maxDistinctNvmeDisks = 0
minDiskCount = 0
minDiskTB = 1800
minDiskIOPS = 0
minDiskStreamMBs = 0
minDiskHddIOPS = 0
minDiskHddTB = 0
minDiskFastIOPS = 0
minDiskFastTB = 0
fillAllDiskSlots = True

# Netowrk
minTotalNetworkSpeedGigabits = 4300
minNetworkConnectionsPerNode = 2
maxNetworkConnections = 10000
maxDistinctNetworkCards = 1
minNetworkCardsPerServer = 1
maxNetworkCardsPerServer = 1
allowSiomCards = False

# Racks
rackCostPerMonth = 2000
serverCostTimeHorizonYears = 0
availableWattsPerRack = 20000
# Used to shut off rack costs
rackCostScalingFactor = 0


bestIlp = ilp()
print(bestIlp)


class Goal:
    def __init__(self, model, name, goal, nWeight=0, pWeight=0, nBound=-1, pBound=-1):
        self.model = model
        self.name = name
        self.goal = goal
        self.negativeDeviationWeight = nWeight
        self.positiveDeviationWeight = pWeight
        self.negativeDeviationBound = nBound
        self.positiveDeviationBound = pBound
        self.negativeDeviation = None
        self.positiveDeviation = None
        self.linExpr = LinExpr()
        self.objective = LinExpr()
        self.min = None
        self.max = None

    def finalize(self):
        if self.min is not None:
            self.model.addConstr(self.linExpr, GRB.GREATER_EQUAL, self.min, "min " + self.name)
        if self.max is not None:
            self.model.addConstr(self.linExpr, GRB.LESS_EQUAL, self.max, "max " + self.name)
        if isinstance(self.goal, LinExpr):
            self.model.addConstr(self.linExpr, GRB.EQUAL, self.goal, "equal " + self.name)
        elif self.goal is not None:
            if self.negativeDeviationBound >= 0:
                self.negativeDeviation = self.model.addVar(lb=0, ub=self.negativeDeviationBound, vtype=GRB.INTEGER, name=self.name + " negative deviation")
            else:
                self.negativeDeviation = self.model.addVar(lb=0, vtype=GRB.INTEGER, name=self.name + " negative deviation")
            if self.positiveDeviationBound >= 0:
                self.positiveDeviation = self.model.addVar(lb=0, ub=self.positiveDeviationBound, vtype=GRB.INTEGER, name=self.name + " positive deviation")
            else:
                self.positiveDeviation = self.model.addVar(lb=0, vtype=GRB.INTEGER, name=self.name + " positive deviation")
            self.linExpr = self.linExpr + self.negativeDeviation - self.positiveDeviation
            self.model.addConstr(self.linExpr, GRB.EQUAL, self.goal, "goal " + self.name)
            if self.goal != 0:
                self.objective = (self.negativeDeviationWeight / float(self.goal)) * self.negativeDeviation + (self.positiveDeviationWeight / float(self.goal)) * self.positiveDeviation
            else:
                self.objective = self.negativeDeviationWeight * self.negativeDeviation + self.positiveDeviationWeight * self.positiveDeviation
        return self.objective

    def add(self, other):
        self.linExpr = self.linExpr + other

    def subtract(self, other):
        self.linExpr = self.linExpr - other

    def setMax(self, expr):
        self.max = expr
        self.goal = None
        return self

    def setMin(self, expr):
        self.min = expr
        self.goal = None
        return self

    def setEqual(self, expr):
        self.goal = expr
        self.negativeDeviationBound = 0
        self.negativeDeviationWeight = 1
        self.positiveDeviationBound = 0
        self.positiveDeviationWeight = 1


class Goals:

    def __init__(self, name):
        m = Model(name)
        self.model = m
        self.cost = Goal(m, "cost", goal=400000, pWeight=4000)  # 432304

        # Servers
        self.distinctServerTypes = Goal(m, "distinctServerTypes", goal=1, pWeight=1, pBound=0)
        self.serverCount = Goal(m, "serverCount", goal=0)
        self.nodeCount = Goal(m, "nodeCount", goal=0)

        # Memory
        # True Constraint
        self.distinctMemoryTypes = Goal(m, "distinctMemoryTypes", goal=1, pWeight=1, pBound=0)
        self.memoryGB = Goal(m, "memoryGB", goal=10240, nWeight=10000000, nBound=1000)
        # self.avgMemoryPerNode = Goal(m, "avgMemoryPerNode", goal=256, nWeight=1, pWeight=1, nBound=128, pBound=3000)

        # Cpus
        self.distinctCpuTypes = Goal(m, "distinctCpuTypes", goal=1, pWeight=1, pBound=0)
        self.cpuCores = Goal(m, "cpuCores", goal=0, nWeight=1000000)
        self.cpuGigaflops = Goal(m, "cpuGigaflops", goal=3000, nWeight=300000, nBound=10000)

        # Disk
        self.distinctDiskTypes = Goal(m, "distinctDiskTypes", goal=2, pWeight=1, pBound=0)
        self.distinct25DiskTypes = Goal(m, "distinct25DiskTypes", goal=1, pWeight=1, pBound=0)
        self.distinct35DiskTypes = Goal(m, "distinct35DiskTypes", goal=1, pWeight=1, pBound=0)
        self.distinctNvmeDiskTypes = Goal(m, "distinctNvmeDiskTypes", goal=0, pBound=0)
        self.diskCount = Goal(m, "diskCount", goal=0, nWeight=1, nBound=0)
        self.disk25Count = Goal(m, "disk25Count", goal=0)
        self.disk35Count = Goal(m, "disk35Count", goal=0)
        self.diskNvmeCount = Goal(m, "diskNvmeCount", goal=0)
        self.diskTB = Goal(m, "diskTB", goal=1800, nWeight=1000000, nBound=1800)
        self.diskIOPS = Goal(m, "diskIOPS", goal=0, nWeight=1)
        self.diskStreamMBs = Goal(m, "streamMBs", goal=10000, nWeight=1, nBound=0)
        self.diskHddIOPS = Goal(m, "diskHddIOPS", goal=0, nWeight=1, nBound=0)
        self.diskHddTB = Goal(m, "diskHddTB", goal=0, nWeight=1, nBound=0)
        self.diskFastIOPS = Goal(m, "diskFastIOPS", goal=0, nWeight=1, nBound=0)
        self.diskFastTB = Goal(m, "diskFastTB", goal=0, nWeight=1, nBound=0)
        self.fillAllDiskSlots = True

        # Network
        self.totalNetworkSpeedGigabits = Goal(m, "totalNetworkSpeedGigabits", 12000, nWeight=1, nBound=0)
        self.minNetworkConnectionsPerNode = 2
        self.networkConnections = Goal(m, "networkConnections", goal=0)
        self.distinctNetworkCardTypes = Goal(m, "distinctNetworkCardTypes", goal=1, pWeight=1, pBound=0)
        self.minNetworkCardsPerNode = 1
        self.maxNetowrkCardsPerNode = 1
        self.allowSiomCards = False

        # Racks
        self.rackUnits = Goal(m, "rackUnits", goal=32)
        self.watts = Goal(m, "watts", goal=0)
        self.racks = Goal(m, "racks", goal=1, pWeight=1)
        self.rackCostPerMonth = 2000
        self.serverCostTimeHorizonYears = 3
        self.availableWattsPerRack = 20000
        # Used to shut off rack costs
        self.rackCostScalingFactor = 0

    def finalize(self):
        allGoals = [attr for attr in dir(self) if isinstance(getattr(self, attr), Goal)]
        objective = LinExpr()
        for goal in allGoals:
            objective = objective + getattr(self, goal).finalize()
        return objective


def goalProgramming(i):
    m = i.model
    cpus, memory, disk25, disk35, diskNvme, siom, pciNetwork, servers, racks = buildVars(m)

    ##### Server #####

    serverCpuSlots = LinExpr()
    serverMemorySlots = LinExpr()
    serverMinMemorySlots = LinExpr()
    server25DiskSlots = LinExpr()
    server35DiskSlots = LinExpr()
    serverNvmeSlots = LinExpr()
    min25Disks = LinExpr()
    min35Disks = LinExpr()
    maxSiomCards = LinExpr()
    maxPciNetworkCards = LinExpr()
    for server in servers:
        i.serverCount.add(server.countVar)
        i.distinctServerTypes.add(server.useVar)
        i.nodeCount.add(server.countVar * server.nodes)
        i.rackUnits.add(server.countVar * server.rackUnits)
        i.watts.add(server.countVar * server.watts)
        i.cost.add(server.countVar * server.configuredCost)

        serverCpuSlots = serverCpuSlots + server.countVar * (server.cpuSlots * server.nodes)
        serverMemorySlots = serverMemorySlots + server.countVar * (server.memorySlots * server.nodes)
        serverMinMemorySlots = serverMinMemorySlots + server.countVar * (server.minMemorySlots * server.nodes)
        server25DiskSlots = server25DiskSlots + server.countVar * (server.disk25Slots * server.nodes)
        min25Disks = min25Disks + server.countVar * (server.minimum25Disks * server.nodes)
        server35DiskSlots = server35DiskSlots + server.countVar * (server.disk35Slots * server.nodes)
        min35Disks = min35Disks + server.countVar * (server.minimum35Disks * server.nodes)
        serverNvmeSlots = serverNvmeSlots + server.countVar * (server.nvmeSlots * server.nodes)
        maxSiomCards = maxSiomCards + server.countVar * (server.siomCards * server.nodes)
        maxPciNetworkCards = maxPciNetworkCards + server.countVar * ((server.pcieV3X16Slots + server.pcieV3X8Slots) * server.nodes)

    ##### Racks #####

    maxRackUnits = LinExpr()
    maxWatts = LinExpr()
    previousRack = None
    for rack in racks:
        if previousRack is not None:
            m.addConstr(rack.useVar, GRB.LESS_EQUAL, previousRack.useVar, "rack {} after rack {}".format(rack, previousRack))
        #previousRack = rack
        i.racks.add(rack.useVar)
        maxRackUnits = maxRackUnits + rack.useVar * rack.availableRackUnits
        maxWatts = maxWatts + rack.useVar * rack.availableWatts
        i.cost.add(rack.useVar * i.rackCostScalingFactor * (rack.networkCost + (rack.costPerMonth * 12 * rack.timeHorizonYears)))

    i.rackUnits.setMax(maxRackUnits)
    i.watts.setMax(maxWatts)

    ##### CPU #####
    cpuCount = LinExpr()
    for cpu in cpus:
        i.distinctCpuTypes.add(cpu.useVar)
        i.cpuCores.add(cpu.countVar * cpu.cores)
        i.cpuGigaflops.add(cpu.countVar * (cpu.cores * cpu.ghz))
        i.cost.add(cpu.countVar * cpu.cost)
        cpuCount = cpuCount + cpu.countVar

    m.addConstr(serverCpuSlots, GRB.EQUAL, cpuCount, "fillCpuSlots")

    ##### Memory #####
    memorySlots = LinExpr()
    for mem in memory:
        i.distinctMemoryTypes.add(mem.useVar)
        i.memoryGB.add(mem.countVar * mem.memoryGB)
        i.cost.add(mem.countVar * mem.cost)
        memorySlots = memorySlots + mem.countVar

    m.addConstr(memorySlots, GRB.LESS_EQUAL, serverMemorySlots, "maxMemorySlotsAvailable")
    m.addConstr(memorySlots, GRB.GREATER_EQUAL, serverMinMemorySlots, "minMemorySlotsRequiredByServers")

    ##### Disk #####
    allDisks = []
    allDisks.extend(disk25)
    allDisks.extend(disk35)
    allDisks.extend(diskNvme)

    for disk in disk25:
        i.disk25Count.add(disk.countVar)
        i.distinct25DiskTypes.add(disk.useVar)
    for disk in disk35:
        i.disk35Count.add(disk.countVar)
        i.distinct35DiskTypes.add(disk.useVar)
    for disk in diskNvme:
        i.diskNvmeCount.add(disk.countVar)
        i.distinctNvmeDiskTypes.add(disk.useVar)

    for disk in allDisks:
        i.distinctDiskTypes.add(disk.useVar)
        i.diskCount.add(disk.countVar)
        i.diskTB.add(disk.countVar * disk.tb)
        i.diskIOPS.add(disk.countVar * disk.iops)
        i.diskStreamMBs.add(disk.countVar * disk.streamMBs)
        i.cost.add(disk.countVar * disk.cost)
        if disk.type == hdd:
            i.diskHddTB.add(disk.countVar * disk.tb)
            i.diskHddIOPS.add(disk.countVar * disk.iops)
        else:
            i.diskFastTB.add(disk.countVar * disk.tb)
            i.diskFastIOPS.add(disk.countVar * disk.iops)

    if i.fillAllDiskSlots:
        i.disk35Count.setEqual(server35DiskSlots)
        i.disk25Count.setEqual(server25DiskSlots)
    else:
        i.disk25Count.setMin(min25Disks).setMax(server25DiskSlots)
        i.disk35Count.setMin(min35Disks).setMax(server35DiskSlots)

    ##### Network #####
    networks = []
    networks.extend(siom)
    networks.extend(pciNetwork)

    networkCards = LinExpr()
    for network in networks:
        networkCards = networkCards + network.countVar
        i.totalNetworkSpeedGigabits.add(network.countVar * (network.speedGbit * network.adapterCount))
        i.networkConnections.add(network.countVar * network.adapterCount)
        i.distinctNetworkCardTypes.add(network.useVar)
        i.cost.add(network.countVar * network.cost)

    siomCardCount = LinExpr()
    for s in siom:
        siomCardCount = siomCardCount + s.countVar

    pciNetworkCount = LinExpr()
    for pci in pciNetwork:
        pciNetworkCount = pciNetworkCount + pci.countVar

    m.addConstr(networkCards, GRB.GREATER_EQUAL, i.nodeCount.linExpr * i.minNetworkCardsPerNode, "minNetworkCardPerNode")
    i.networkConnections.setMin(i.minNetworkConnectionsPerNode * i.nodeCount.linExpr)
    m.addConstr(siomCardCount, GRB.LESS_EQUAL, maxSiomCards if allowSiomCards else 0, "maxSiomCards")
    m.addConstr(pciNetworkCount, GRB.LESS_EQUAL, maxPciNetworkCards, "maxPciNetworkCards")

    ##### Objective #####

    objective = i.finalize()

    m.setObjective(objective, GRB.MINIMIZE)

    m.optimize()

    m.write("goalModel.lp")

    for v in m.getVars():
        if abs(v.X) > 1e-6 and not v.varName.startswith("use "):
            print (v.varName, int(round(v.X, 0)))
    return m.getAttr("ObjVal")


# goals = Goals("goalProgramming")
# bestGoals = goalProgramming(goals)
# print("best optimization function = {}".format(bestGoals))
