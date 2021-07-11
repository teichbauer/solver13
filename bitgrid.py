from basics import set_bit
from vklause import VKlause


class BitGrid:
    def __init__(self, grid_bits):
        # grid-bits: high -> low, descending order
        self.grids = list(reversed(grid_bits))  # bits

    def vary_1bit(self, val, bits, cvs=None):
        if cvs == None:
            cvs = []
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
        cvs = None
        v = 0
        out_dic = {}
        for b in vk.dic:
            if b in self.grids:
                ind = self.grids.index(b)  # self.bits: descending order
                g.remove(ind)
                v = set_bit(v, ind, vk.dic[b])
            else:
                out_dic[b] = vk.dic[b]
        if len(out_dic) == 0:  # vk covers all 3 bits
            # return vk's compressed-value(not a list), and None
            return vk.compressed_value(), None

        ovk = VKlause(vk.kname, out_dic, vk.nov)
        if len(out_dic) < 3:
            cvs = self.vary_1bit(v, g)
            cvs.sort()

        return cvs, ovk
