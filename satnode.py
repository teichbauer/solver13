# from typing_extensions import ParamSpecKwargs
from vk12mgr import VK12Manager
from basics import get_bit
from satholder import SatHolder
from pathmgr import PathManager
from bitgrid import BitGrid
from center import Center


class SatNode:
    debug = False
    # debug = True

    def __init__(self, parent, sh, vkm, choice):
        self.parent = parent
        self.sh = sh
        self.vkm = vkm
        self.nov = vkm.nov
        self.next = None
        self.done = False
        self.choice = choice
        self.bitgrid = BitGrid(self.choice)
        self.prepare()
        Center.snodes[self.nov] = self

    def prepare(self):
        self.make_skeleton()
        self.vk12dic = {}  # store all vk12s, all tnode's vkdic ref to here
        self.next_sh = self.sh.reduce(self.choice["bits"])
        self.next_vkm, self.chdic = self.vkm.morph(self)  # next_vkm: all vk3s
        self.done = (self.next_vkm == None) or len(self.next_vkm.vkdic) == 0

        if self.debug:
            ks = [f"{self.nov}.{k}" for k in self.chdic.keys()]
            print(f"keys: {ks}")
        if self.done:
            for nov, sn in Center.snodes.items():
                pass

    # end of def prepare(self):

    def spawn(self):
        # print(f'snode-nov{self.nov}')
        # after morph, vkm.vkdic only have vk3s left, if any
        if len(self.chdic) == 0:
            self.done = True
            return None
        else:
            self.next = SatNode(
                self, self.next_sh.clone(), self.next_vkm, self.next_choice
            )
            return self.next

    def make_skeleton(self):
        thsats = Center.skeleton.setdefault(self.nov, {})
        cvrs = []
        for bvk in self.choice["ancvks"]:
            cvrs.append(bvk.compressed_value())
        for v in range(8):
            if v not in cvrs:
                hsat = thsats.setdefault(v, {})
                for indx, b in enumerate(self.choice["bits"]):
                    hsat[b] = get_bit(v, 2 - indx)

    def set_topdowns(self, tnode, bits):
        td_dic = Center.topdowns.setdefault(self.nov, {})
        novs = sorted(Center.skeleton.keys(), reverse=True)
        ind = novs.index(self.nov)
        for nov in novs[ind + 1 :]:
            tname = f"{nov}."
            # bset = Center.snodes[nov].choice['bit_set']
            for vk in tnode.vkm.vkdic.values():
                lst = bits[:]  # [25,7,1]
                vk.compressed_value(lst)
                ss = bset.intersection(vk.bits)
                if len(ss) > 0:
                    if set(vk.bits) == ss:
                        vkv = vk.compressed_value()
                    else:
                        pass

                    pass
                else:
                    pass

            sdics = Center.skeleton[nov]
            for v, sdic in sdics.items():
                tname += f"{v}"
                add_it = True
                td_vkm = VK12Manager(Center.maxnov)
                for kn, vk in tnode.vkm.vkdic.items():
                    ttl_hit, v12 = vk.partial_hit_residue(sdic)
                    if ttl_hit:
                        add_it = False
                        break
                    elif v12:
                        td_vkm.add_vk(v12)
                        if not td_vkm.valid:
                            add_it = False
                            break
                if add_it:
                    td_dic[v] = td_vkm

    def make_paths(self):
        if not self.parent:  # do nothing for top-level snode
            return
        # collect higher-chs, and the ones being refed by this snode
        higher_vals_inuse = set([])
        dels = []  # for collecting tnode with no path
        for val, tnode in self.chdic.items():
            tnode.pthmgr = PathManager(tnode, self.done)
            if len(tnode.pthmgr.dic) == 0:
                dels.append(tnode)
            else:
                high_vals = [int(k[1].split(".")[1]) for k in tnode.pthmgr.dic]
                higher_vals_inuse.update(high_vals)
        # clean-up ch-tnodes, if its pthmgr.dic is empty
        for tnode in dels:
            self.chdic.pop(tnode.val)
            Center.repo.pop(tnode.name, None)
        self.done = len(self.chdic) == 0
        # clean-up higher-chs not being used by any tnode
        self.parent.trim_chs(higher_vals_inuse)

    def trim_chs(self, used_vals):
        """the chdic keys not in used_vals(a set), will be deleted. if this
        changs used val-set of parent level, recursiv-call on parent"""
        s = set(self.chdic.keys())
        if s != used_vals:
            delta = s - used_vals
            for v in delta:
                tn = self.chdic.pop(v, None)
                if tn:
                    Center.repo.pop(tn.name, None)
            if self.parent:
                # recursive call of parent.trim_chs
                higher_vals_inuse = set([])
                for tn in self.chdic.values():
                    vs = [int(k[1].split(".")[1]) for k in tn.pthmgr.dic]
                    higher_vals_inuse.update(vs)
                self.parent.trim_chs(higher_vals_inuse)

    def is_top(self):
        return self.nov == Center.maxnov

    def solve(self):
        return Center.sats

    def update_cnt(self):
        cnts = {}
        for nov, sn in Center.snodes.items():
            if nov < Center.maxnov:
                cnt = {v: len(tn.pthmgr.dic.keys()) for v, tn in sn.chdic.items()}
                cnts[nov] = cnt
        return cnts
