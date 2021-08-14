# from typing_extensions import ParamSpecKwargs
from vk12mgr import VK12Manager
from basics import get_bit
from vklause import VKlause
from pathmgr import PathManager
from bitgrid import BitGrid
from center import Center


class SatNode:
    debug = False
    # debug = True

    def __init__(self, parent, sh, vkm, choice):
        self.parent = parent
        if parent:
            self.nov = parent.nov - 3
        else:
            self.nov = Center.maxnov
        self.sh = sh
        self.vkm = vkm
        # holds the best-covering-vks from vkm.vkdic
        self.bvks = []
        self.next = None
        self.done = False
        self.choice = choice
        self.bvks = tuple(vkm.pop_vk(vk.kname) for vk in choice["ancvks"])
        self.bitgrid = BitGrid(self)
        self.prepare()
        Center.snodes[self.nov] = self

    def prepare(self):
        # self.make_skeleton()
        self.vk12dic = {}  # store all vk12s, all tnode's vkdic ref to here
        self.next_sh = self.sh.reduce(self.choice["bits"])
        self.chdic = self.vkm.morph(self)  # next_vkm: all vk3s
        if self.nov == 24:
            Center.save_pathdic('path-info.json')

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
            self.next = SatNode(self,
                                self.next_sh.clone(),
                                self.vkm,
                                self.next_choice
                                )
            return self.next

    def split_vkm(self):
        # pop-out touched-vk3s forming vk12dic with them
        # tdic: keyed by cvs of vks and values are lists of vks
        # make next-choice from vkm - if not empty, if it is empty, done=True
        tdic = {}
        for kn in self.choice['touched']:
            vk = self.vkm.pop_vk(kn)
            cvs, rvk = self.bitgrid.cvs_and_outdic(vk)
            for v in cvs:
                if v not in self.bitgrid.covers:
                    s = tdic.setdefault(v, set([]))
                    s.add(rvk)
                if kn not in self.vk12dic:
                    self.vk12dic[kn] = rvk
        grps = {v: {} for v in tdic}
        for v in tdic:
            for vk2 in tdic[v]:
                grps[v][vk2.kname] = vk2

        if len(self.vkm.vkdic) == 0:
            self.done = True
            self.next_choice = None
        else:
            self.next_choice = self.vkm.choose_anchor()
        # return tdic
        return grps

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
                cnt = {v: len(tn.pthmgr.dic.keys())
                       for v, tn in sn.chdic.items()}
                cnts[nov] = cnt
        return cnts
