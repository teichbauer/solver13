from basics import set_bit
from vklause import VKlause


class BitGrid:
    def __init__(self, snode):  # grid_bits):
        # grid-bits: high -> low, descending order
        self.grids = tuple(reversed(snode.choice["bits"]))  # bits
        self.covers = tuple(vk.compressed_value() for vk in snode.bvks)
        self.chheads = tuple(v for v in range(8) if v not in self.covers)

    def find_vkgrps(self, tnode):
        grps = {}
        for v in self.chheads:
            grps[v] = tnode.vkm.vkdic.copy()
        ss = set(self.grids).intersection(set(tnode.vkm.bdic))
        if len(ss) == 0:  # bit-grid not touched by tnode.vkm.bdic
            return grps   # every grps[v] has the same copy of vkdic from tnode

        # bit-grid has intersection of bits with tnode.vkm
        for vk_bit in ss:
            for kn in tnode.vkm.bdic[vk_bit]:
                vk = tnode.vkm.vkdic[kn]
                cvs, odic = self.cvs_and_outdic(vk)
                for v in self.chheads:
                    if v in grps:
                        if v in cvs:
                            if len(odic):
                                grps[v][kn] = VKlause(kn, odic)
                            else:  # odic empty -> vk hit by bit-grid
                                grps.pop(v)
                        else:  # for v not in cvs: remove kn/vk
                            grps[v].pop(kn)
        return grps

        '''
        grps = {v: {} for v in self.chheads}
        for kn, vk in tnode.vkm.vkdic.items():
            cvs, odic = self.cvs_and_outdic(vk)
            if len(odic) == 0:
                for v in cvs:
                    grps.pop(v, None)
            elif len(cvs) > 0:
                for v in cvs:
                    grps[v] = VKlause(kn, odic)
            else:  # len(cvs) == 0: vk lies totally outside of bit-grid
                for v in grps:
                    grps[v][kn] = vk
        return grps
        '''

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
            if b in self.grids:
                ind = self.grids.index(b)  # self.bits: descending order
                g.remove(ind)
                v = set_bit(v, ind, vk.dic[b])
            else:
                out_dic[b] = vk.dic[b]
        odic_ln = len(out_dic)
        if odic_ln == 0:  # vk is covered by grid-3 bits totally
            # there is no rvk (None)
            if vk.nob == 3:   # cvs is a single value, not a list
                cvs = vk.compressed_value()
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
