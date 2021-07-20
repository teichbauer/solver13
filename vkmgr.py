from basics import print_json
from vklause import VKlause
from tnode import TNode
from center import Center


class VKManager:
    def __init__(self, vkdic, initial=False):
        self.vkdic = vkdic
        if initial:
            self.make_bdic()

    def clone(self):
        vkdic = {kn: vk.clone() for kn, vk in self.vkdic.items()}
        vkm = VKManager(vkdic)
        vkm.bdic = {b: s.copy() for b, s in self.bdic.items()}

    def pop_vk(self, kn):
        vk = self.vkdic.pop(kn)
        for bit in vk.bits:
            if kn in self.bdic[bit]:
                self.bdic[bit].remove(kn)
            else:
                raise Exception(f"pop {kn} failed")
        return vk

    def printjson(self, filename):
        print_json(self.nov, self.vkdic, filename)

    def make_bdic(self):
        self.bdic = {}
        for kn, vk in self.vkdic.items():
            for b in vk.dic:
                if b not in self.bdic:  # hope this is faster than
                    self.bdic[b] = set([])  # bdic.setdefault(b,set([]))
                self.bdic[b].add(kn)

    def morph(self, snode):
        tdic = snode.split_vkm()
        pthdic = {}
        if snode.parent:
            vdic = {}
            for pv, ctnode in snode.parent.chdic.items():
                vdic[f"{snode.parent.nov}.{pv}"] = ctnode.approve(
                    snode.bitgrid)

            for ky, vk12mdic in vdic.items():
                for tv, vkm in vk12mdic.items():
                    tmpdic = pthdic.setdefault(tv, {})
                    tmpdic[ky] = vkm

        for val in tdic:
            sub_vk12dic = {}
            if val in tdic:  # touched kn/kv does have outside bit
                vk2s = tdic[val]
                for vk2 in vk2s:
                    sub_vk12dic[vk2.kname] = vk2
            # print(f'child-{val}')
            tnode = TNode(sub_vk12dic, snode, val)
            if tnode.vkm.valid:
                Center.repo[tnode.name] = tnode
                pthdic[val] = tnode
        # re-make self.bdic, based on updated vkdic (now all 3-bit vks)
        # for making chdic with tnodes
        return pthdic

    # enf of def morph()

    def choose_anchor(self):
        "return: {'ancs': (tkn1, tkn2,),'bits': bits[,,],'touched':[,,..,]}"
        best_choice = None
        max_tsleng = -1
        max_tcleng = -1
        best_bits = None
        kns = set(self.vkdic.keys())  # candidates-set of kn for besy-key
        while len(kns) > 0:
            kn = kns.pop()
            vk = self.vkdic[kn]
            # sh_sets: {<bit>:<set of kns sharing this bit>,..} for each vk-bit
            sh_sets = {}  # dict keyed by bit, value is a set of kns on the bit
            bits = vk.bits
            for b in bits:
                sh_sets[b] = self.bdic[b].copy()
            # dict.popitem() pops a tuple: (<key>,<value>) from dict
            tsvk = sh_sets.popitem()[1]  # [0] is the bit/key, [1] is the set
            tcvk = tsvk.copy()
            for s in sh_sets.values():
                tsvk = tsvk.intersection(s)
                tcvk = tcvk.union(s)

            chc = (tsvk, tcvk - tsvk)
            kns -= tsvk  # take kns in tsvk out of candidates-set
            ltsvk = len(tsvk)
            if ltsvk < max_tsleng:
                continue
            ltcvk = len(tcvk)
            if not best_choice:
                best_choice = chc
                max_tsleng = ltsvk
                max_tcleng = ltcvk
                best_bits = bits
                # best_bitsum = sum(bits)
            else:
                if best_choice[0] == tsvk:
                    continue
                # see if to replace the best_choice?
                replace = False
                if max_tsleng < ltsvk:
                    replace = True
                elif max_tsleng == ltsvk:
                    if max_tcleng < ltcvk:
                        replace = True
                    elif max_tcleng == ltcvk:
                        if bits > best_bits:
                            replace = True
                if replace:
                    best_choice = chc
                    max_tsleng = ltsvk
                    max_tcleng = ltcvk
                    best_bits = bits
        result = {
            "ancvks": [self.vkdic[kn] for kn in best_choice[0]],
            "touched": best_choice[1],
            "bits": best_bits,
        }
        return result

    # end of def choose_anchor(self):
