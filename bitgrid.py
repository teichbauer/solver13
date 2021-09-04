from basics import set_bit
from vklause import VKlause


class BitGrid:
    BDICS = {
        0: {2: 0, 1: 0, 0: 0},
        1: {2: 0, 1: 0, 0: 1},
        2: {2: 0, 1: 1, 0: 0},
        3: {2: 0, 1: 1, 0: 1},
        4: {2: 1, 1: 0, 0: 0},
        5: {2: 1, 1: 0, 0: 1},
        6: {2: 1, 1: 1, 0: 0},
        7: {2: 1, 1: 1, 0: 1},
    }

    def __init__(self, choice):  # grid_bits):
        # grid-bits: high -> low, descending order
        self.bits = tuple(reversed(choice["bits"]))  # bits
        self.bitset = set(choice["bits"])
        self.avks = choice["avks"]
        self.covers = tuple(vk.cmprssd_value() for vk in self.avks)
        self.chheads = tuple(v for v in range(8) if v not in self.covers)

    def violated(self, vkdic):
        for vk in vkdic.values():
            pass
        return False

    def grid_sat(self, val):
        return {self.bits[b]: v for b, v in self.BDICS[val].items()}

    def hit(self, satdic):
        for avk in self.avks:
            if avk.hit(satdic):
                return True
        return False

    def reduce_cvs(self, vk12m):
        """ for every vk in vk12m.vkdic, if vk is totally within grid,
            """
        cvs_set = set(self.chheads)
        kns = vk12m.kn1s + vk12m.kn2s
        for kn in kns:
            if self.bitset.issuperset(vk12m.vkdic[kn].bits):
                pass

    def tn_grps(self, tnode):
        grps = {}
        for v in self.chheads:
            grps[v] = tnode.vkm.vkdic.copy()
        ss = self.bitset.intersection(tnode.vkm.bdic)
        if len(ss) == 0:  # bit-grid not touched by tnode.vkm.bdic
            return grps  # every grps[v] has the same copy of vkdic from tnode
        # bit-grid has intersection of bits with tnode.vkm
        # a kn/vk needs to be handled only once. If a kn has been handled
        handled_kns = []  # it can then be jumped over
        for vk_bit in ss:
            for kn in tnode.vkm.bdic[vk_bit]:
                if kn in handled_kns:
                    continue
                else:
                    handled_kns.append(kn)
                cvs, odic = self.cvs_and_outdic(tnode.vkm.vkdic[kn])
                if (kn in tnode.vkm.kn1s) or len(odic) == 0:
                    for v in self.chheads:
                        if v in grps:
                            if v in cvs:
                                grps.pop(v, None)
                            else:
                                grps[v].pop(kn, None)
                else:  # vk2 with 1 bit in 1 bit out of grid
                    new_vk = VKlause(kn, odic)
                    for v in self.chheads:
                        if v in grps:
                            if v in cvs:
                                grps[v][kn] = new_vk
                            else:
                                grps[v].pop(kn, None)
        return grps

    def vary_1bit(self, val, bits, cvs):
        if len(bits) == 0:
            cvs.append(val)
        else:
            bit = bits.pop()
            for v in (0, 1):
                nval = set_bit(val, bit, v)
                if len(bits) == 0:
                    cvs.append(nval)
                else:
                    self.vary_1bit(nval, bits[:], cvs)
        return cvs

    def cvs_and_outdic(self, vk):
        g = [2, 1, 0]
        cvs = []
        # vk's dic values within self.grid-bits, forming a value in (0..7)
        # example: grids: (16,6,1), vk.dic:{29:0, 16:1, 1:0} has
        # {16:1,1:0} iwithin grid-bits, forming a value of 4/1*0 where
        # * is the variable value taking 0/1 - that will be set by
        # self.vary_1bit call, but for to begin, set v to be 4/100
        v = 0
        out_dic = {}
        for b in vk.dic:
            if b in self.bits:
                ind = self.bits.index(b)  # self.bits: descending order
                g.remove(ind)
                v = set_bit(v, ind, vk.dic[b])
            else:
                out_dic[b] = vk.dic[b]
        odic_ln = len(out_dic)
        if odic_ln == 0:  # vk is covered by grid-3 bits totally
            # there is no rvk (None)
            if vk.nob == 3:   # cvs is a single value, not a list
                cvs = vk.cmprssd_value()
            elif vk.nob < 3:  # cvs is a list of values
                cvs = self.vary_1bit(v, g, cvs)  # TB verified
            return cvs, None

        # ovk = VKlause(vk.kname, out_dic)
        if odic_ln == 3:
            raise Exception("vk3!")

        if odic_ln != vk.nob:
            # get values of all possible settings of untouched bits in g
            cvs = self.vary_1bit(v, g, cvs)
            cvs.sort()
        # else: # in case of len(out_dic) == 3
        # cvs remains None, ovk is a vk3 (untouched by grid-bits)
        # return cvs, ovk
        return cvs, out_dic
