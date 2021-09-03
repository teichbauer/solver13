from vk12mgr import VK12Manager
from center import Center


class TNode:
    # def __init__(self, vk12dic, holder_snode, val):
    def __init__(self, vk12m, holder_snode, name):
        self.holder = holder_snode
        # self.sh = holder_snode.next_sh
        self.name = name
        # self.hsat = holder_snode.sh.get_sats(val)
        self.vkm = vk12m
        # self.vkm = VK12Manager(vk12dic)

    def get_nsat(self):
        sat = {}
        names = self.name.split('-')
        for name in names:
            nov, val = name.split('.')
            snode = Center.snodes[int(nov)]
            sat.update(snode.bgrid.grid_sat(int(val)))
        return sat

    def get_rsats(self, bgrid):
        rsats = []
        sat0 = {}
        rbits = Center.bits.copy()
        for kn in self.vkm.kn1s:
            vk = self.vkm.vkdic[kn]
            b, v = vk.hbit_value()
            sat0[b] = int(not v)
            rbits.remove(b)
        for kn in self.vkm.kn2s:
            x = 1
            pass
        if len(rbits) > 0:
            while len(rbits) > 0:
                rb = rbits.pop()
                for v in (0, 1):
                    sat = sat0.copy()
                    sat[rb] = v
                    if not bgrid.hit(sat):
                        rsats.append(sat)
        elif not bgrid.hit(sat0):
            rsats.append(sat0)
        return rsats

    def get_sats(self, last_bgrid):
        sats = []
        rsats = self.get_rsats(last_bgrid)
        nsat = self.get_nsat()
        if len(rsats) > 0:
            for sat in rsats:
                sat.update(nsat)
                sats.append(sat)
        Center.sats += sats
