

sas = 'SAS'
sata = 'SATA'
hdd = 'HDD'
ssd = 'SSD'
nvme = 'NVME'
ddr4 = 'DDR4'
ddr3 = 'DDR3'
dom = 'DOM' #disk on module
domssd = dom + ssd



class Cpu:
    cores = 0
    ghz = 0
    cacheMB = 0
    watts = 0
    cost = 0
    family = 'xeon'
    name = ''

    def __init__(self, cores, ghz, cost, name, cachemb = 0, watts = 0, family = 'xeon'):
        self.cores = cores
        self.ghz = ghz
        self.cost = cost
        self.name = name
        self.cacheMB = cachemb
        self.watts = watts
        self.family = family

    @staticmethod
    def default():
        return Cpu(0, 0, 0, '', 0, 0, 'unknown')


cpu = [Cpu(6, 1.7, 249, 'E5 - 2603', 15, 85),
       Cpu(8, 1.7, 369, 'E5 - 2609', 20, 85),
       Cpu(8, 2.1, 499, 'E5 - 2620', 20, 85),
       Cpu(10, 2.2, 769, 'E5 - 2630', 25, 85),
       Cpu(10, 2.4, 1079, 'E5 - 2640', 25, 90),
       Cpu(12, 2.2, 1299, 'E5 - 2650', 30, 105),
       Cpu(14, 2, 1599, 'E5 - 2660', 35, 105),
       Cpu(14, 2.4, 1999, 'E5 - 2680', 35, 120),
       Cpu(14, 2.6, 2349, 'E5 - 2690', 35, 135),
       Cpu(10, 1.8, 729, 'E5 - 2630L', 25, 55),
       Cpu(14, 1.7, 1499, 'E5 - 2650L', 35, 65),
       Cpu(4, 2.6, 509, 'E5 - 2623', 10, 85),
       Cpu(4, 3.5, 1149, 'E5 - 2637', 15, 135),
       Cpu(6, 3.4, 1799, 'E5 - 2643', 20, 135),
       Cpu(8, 3.2, 2349, 'E5 - 2667', 25, 135),
       Cpu(16, 2.1, 1999, 'E5 - 2683', 40, 120),
       Cpu(18, 2.1, 2699, 'E5 - 2695', 45, 120),
       Cpu(16, 2.6, 3249, 'E5 - 2697A', 40, 145),
       Cpu(18, 2.3, 2999, 'E5 - 2697', 45, 145),
       Cpu(20, 2.2, 3599, 'E5 - 2698', 50, 135),
       Cpu(22, 2.2, 4599, 'E5 - 2699', 55, 145),
       Cpu(22, 2.4, 5499, 'E5 - 2699A', 55, 145)]

class Memory:
    memoryGB = 0
    ddrType = str()
    type = str()
    MHz = 0
    cost = 0

    def __init__(self, gb, memoryType, mhz, cost, ddr='DDR4'):
        self.memoryGB = gb
        self.type = memoryType
        self.MHz = mhz
        self.cost = cost
        self.ddrType = ddr

    @staticmethod
    def default():
        return Memory(0, 'unknown', 0, 0)


memory = [  # Memory(4, 'Registered', 2400, 69),
            # Memory(8, 'Registered', 2400, 139),
          Memory(16, 'Registered', 2400, 229),
          Memory(32, 'Registered', 2400, 399),
          Memory(32, 'Load - Reduced', 2400, 479),
          Memory(64, 'Load - Reduced', 2400, 999)]


class Disk:
    tb = 0
    iops = 0
    type = "HDD"
    size = 2.5
    protocol = "SATA"
    gbps = 6
    partNumber = ""
    cost = 0

    def __init__(self, tb, size, cost, iops, protocol, gbps, partnumber, disktype='HDD'):
        self.tb = tb
        self.iops = iops
        self.type = disktype
        self.size = size
        self.protocol = protocol
        self.gbps = gbps
        self.partNumber = partnumber
        self.cost = cost

    @staticmethod
    def default():
        return Disk(0, 0, 0, 0, sata, 0, 'unknown')


disk = [Disk(5, 2.5, 213, 90, sata, 6, 'Barracuda5TB5400'),
        # Disk(.3, 2.5, 189, 166, sas, 12, '0B28810'),
        # Disk(.6, 2.5, 239, 166, sas, 12, '0B28808'),
        # Disk(.9, 2.5, 309, 166, sas, 12, '0B27976'),
        # Disk(1.2, 2.5, 339, 166, sas, 12, '0B28807'),
        # Disk(.3, 2.5, 269, 250, sas, 12, '0B28955'),
        # Disk(.6, 2.5, 399, 250, sas, 12, '0B28953'),
        Disk(1, 2.5, 209, 120, sata, 6, 'ST1000NX0313'),
        Disk(2, 2.5, 349, 120, sata, 6, 'ST2000NX0253'),
        Disk(1, 2.5, 229, 120, sas, 12, 'ST1000NX0333'),
        Disk(2, 2.5, 389, 120, sas, 12, 'ST2000NX0273'),
        # Disk(.6, 2.5, 189, 166, sas, 12, 'ST600MM0018'),
        # Disk(.9, 2.5, 299, 166, sas, 12, 'ST900MM0018'),
        Disk(1.2, 2.5, 339, 166, sas, 12, 'ST1200MM0018'),
        Disk(1.8, 2.5, 439, 166, sas, 12, 'ST1800MM0018'),
        # Disk(.3, 2.5, 249, 250, sas, 12, 'ST300MP0005'),
        # Disk(.6, 2.5, 359, 250, sas, 12, 'ST600MP0005'),
        Disk(2, 3.5, 149, 120, sata, 6, '0F23092'),
        Disk(4, 3.5, 199, 120, sata, 6, '0F23090'),
        Disk(6, 3.5, 239, 120, sata, 6, '0F23001'),
        Disk(8, 3.5, 339, 120, sata, 6, '0F23267'),
        Disk(10, 3.5, 399, 120, sata, 6, '0F27604'),
        Disk(12, 3.5, 589, 120, sata, 6, '0F30144'),
        Disk(2, 3.5, 179, 120, sas, 12, '0F22799'),
        Disk(4, 3.5, 219, 120, sas, 12, '0F22795'),
        Disk(6, 3.5, 259, 120, sas, 12, '0F22791'),
        Disk(8, 3.5, 369, 120, sas, 12, '0F23268'),
        Disk(10, 3.5, 429, 120, sas, 12, '0F27352'),
        Disk(12, 3.5, 609, 120, sas, 12, '0F27352'),
        Disk(1, 3.5, 119, 120, sata, 6, 'ST1000NM0055'),
        Disk(2, 3.5, 139, 120, sata, 6, 'ST2000NM0055'),
        Disk(4, 3.5, 209, 120, sata, 6, 'ST4000NM0035'),
        Disk(6, 3.5, 269, 120, sata, 6, 'ST6000NM0115'),
        Disk(8, 3.5, 339, 120, sata, 6, 'ST8000NM0055'),
        Disk(10, 3.5, 439, 120, sata, 6, 'ST10000NM0086'),
        Disk(12, 3.5, 569, 120, sata, 6, 'ST12000NM0007'),
        Disk(1, 3.5, 139, 120, sas, 12, 'ST1000NM0045'),
        Disk(2, 3.5, 169, 120, sas, 12, 'ST2000NM0045'),
        Disk(4, 3.5, 219, 120, sas, 12, 'ST4000NM0025'),
        Disk(6, 3.5, 259, 120, sas, 12, 'ST6000NM0095'),
        Disk(8, 3.5, 329, 120, sas, 12, 'ST8000NM0075'),
        Disk(10, 3.5, 449, 120, sas, 12, 'ST10000NM0096'),
        Disk(12, 3.5, 529, 120, sas, 12, 'ST12000NM0027'),
        # Disk(1, 3.5, 209, 120, sata, 6, 'ST1000NX0313'),
        # Disk(2, 3.5, 349, 120, sata, 6, 'ST2000NX0253')
        ]


class Server:
    name = "unknown"
    url = ""
    cost = 0
    powerSupplies = 2
    watts = 0
    rackUnits = 1
    osDisks = 2
    osDiskType = 'dom'
    cpu = Cpu.default()
    cpuSlots = 2
    memory = Memory.default()
    memorySlots = 0
    disk = Disk.default()
    diskSlots = 0
    diskSize = 2.5
    minimumDisks = 0
    pcieV3X16Slots = 0
    pcieV3X8Slots = 0
    onBoardNetworkPorts = 0
    nodes = 1
    configuredCost = 0

    def __init__(self, name, url, cost, watts, rackunits, cpuslots, memoryslots, diskslots, disksize, minimumdisks, osdisks, osdisktype, x16, x8, onboardnetworkports, powersupplies, nodes=1):
        self.name = name
        self.url = url
        self.cost = cost
        self.watts = watts
        self.rackUnits = rackunits
        self.cpuSlots = cpuslots
        self.memorySlots = memoryslots
        self.diskSlots = diskslots
        self.minimumDisks = minimumdisks
        self.diskSize = disksize
        self.osDisks = osdisks
        self.osDiskType = osdisktype
        self.pcieV3X16Slots = x16
        self.pcieV3X8Slots = x8
        self.onBoardNetworkPorts = onboardnetworkports
        self.powerSupplies = powersupplies
        self.nodes = nodes

        if x16 > 0:
            networkCost = 1007 * nodes
        elif x8 > 0:
            networkCost = 617 * nodes
        else:
            networkCost = 1007

        supportCost = 450
        self.configuredCost = cost + 139 * osdisks + networkCost + supportCost

    def __str__(self):
        return self.name + ":" + str(self.configuredCost)

    def duplicate(self):
        s = Server(self.name, self.url, self.cost, self.watts, self.rackUnits, self.cpuSlots, self.memorySlots,
                   self.diskSlots, self.minimumDisks, self.osDisks, self.diskSize, self.osDiskType, self.pcieV3X16Slots,
                   self.pcieV3X8Slots, self.onBoardNetworkPorts, self.powerSupplies)
        s.cpu = self.cpu
        s.memory = self.memory
        s.disk = self.disk
        return s


servers = [Server("48x2.5", "https://www.thinkmate.com/product/supermicro/ssg-2028r-e1cr48n", 4146, 1600, 2, 2, 24, 48, 2.5, 24, 2, domssd, 2, 1, 2, 2),
           Server("24x2.5", "https://www.thinkmate.com/product/supermicro/ssg-2028r-e1cr24h", 2441, 920, 2, 2, 16, 24, 2.5, 0, 2, domssd, 1, 6, 2, 2),
           Server("24x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6028r-e1cr24n", 3705, 1600, 2, 2, 24, 24, 3.5, 12, 2, domssd, 2, 1, 0, 2),
           Server("16x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6028r-e1cr16t", 2391, 1000, 2, 2, 16, 16, 3.5, 0, 2, domssd, 1, 6, 2, 2),
           Server("16x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6038r-e1cr16h", 2437, 920, 3, 2, 16, 16, 3.5, 0, 2, domssd, 1, 6, 2, 2),
           Server("90x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6048r-e1cr90l", 8774, 1000, 4, 2, 8, 90, 3.5, 45, 2, domssd, 0, 0, 4, 2),
           Server("72x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6048r-e1cr72l", 8689, 2000, 4, 2, 16, 72, 3.5, 36, 2, domssd, 1, 3, 2, 2),
           Server("60x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6048r-e1cr60n", 5353, 2000, 4, 2, 24, 60, 3.5, 30, 2, dom, 2, 1, 0, 2),  # has 6x nvme external drives optional
           Server("36x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6048r-e1cr36n", 3480, 1280, 4, 2, 24, 36, 3.5, 0, 2, dom, 1, 6, 4, 2),
           Server("24x3.5", "https://www.thinkmate.com/product/supermicro/ssg-6048r-e1cr24n", 2892, 920, 4, 2, 24, 24, 3.5, 0, 2, domssd, 1, 3, 4, 2),
           Server("24x3.5 4 Node", "https://www.thinkmate.com/product/supermicro/sys-2028tp-hc1r-siom", 4685, 2000, 2, 8, 64, 24, 2.5, 4, 1, dom, 4, 4, 0, 2, 4),
           Server("8x2.5 2 Node", "https://www.thinkmate.com/product/supermicro/sys-1028tp-dc1tr", 2718, 1000, 1, 4, 32, 8, 2.5, 0, 1, dom, 1, 0, 2, 2, 2),
           Server("24x2.5 2 Node", "https://www.thinkmate.com/product/supermicro/sys-2028tp-dc1tr", 2989, 1280, 2, 4, 32, 24, 2.5, 0, 1, dom, 2, 2, 2, 2, 2),
           Server("16x2.5 2 Node", "https://www.thinkmate.com/product/supermicro/sys-2028tp-dttr", 2632, 1280, 2, 4, 32, 16, 2.5, 0, 1, dom, 2, 1, 2, 2, 2),  # one x16 can handle a gpu
           Server("12x3.5", "https://www.thinkmate.com/product/supermicro/sys-6028r-tdwnr", 1623, 920, 2, 2, 16, 12, 3.5, 0, 2, dom, 0, 4, 2, 2)]

print(servers)