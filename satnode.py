# from typing_extensions import ParamSpecKwargs
from vklause import VKlause
from vk12mgr import VK12Manager
from basics import get_bit
from tnode import TNode
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
        Center.snodes[self.nov] = self
        self.next = None
        self.done = False
        self.choice = choice
        self.next_sh = self.sh.reduce(self.choice["bits"])
        self.bgrid = BitGrid(self)
        self.split_vkm()

    def spawn(self):
        self.chdic = {}
        if not self.next:
            self.solve()
            return Center.sats

        for gv in self.vk2grps:
            vkm = VK12Manager(self.vk2grps[gv])
            if not vkm.valid:
                continue

            if self.parent:
                dic = self.chdic.setdefault(gv, {})
                name0 = f"{self.nov}.{gv}-"
                for pv, ptnode in self.parent.chdic.items():
                    if type(ptnode).__name__ == 'TNode':
                        if gv in ptnode.grps:
                            vkmx = vkm.clone()
                            if vkmx.add_vkdic(ptnode.grps[gv]):
                                tnname = name0 + ptnode.name
                                tn = TNode(vkmx, self, tnname)
                                dic[tnname] = tn
                                if self.next:
                                    tn.grps = self.next.bgrid.tn_grps(tn)
                                    grps = self.next.bgrid.tn_grps0(tn)
                                    x = 1
                    elif type(ptnode).__name__ == 'dict':
                        for ky, tnd in ptnode.items():
                            if gv in tnd.grps:
                                vkmx = vkm.clone()
                                if vkmx.add_vkdic(tnd.grps[gv]):
                                    tnname = name0 + ky
                                    tn = TNode(vkmx, self, tnname)
                                    dic[tnname] = tn
                                    if self.next:
                                        tn.grps = self.next.bgrid.tn_grps(tn)
                                        grps = self.next.bgrid.tn_grps0(tn)
                                        x = 1
            else:
                tnode = TNode(vkm, self, f"{self.nov}.{gv}")
                if self.next:
                    tnode.grps = self.next.bgrid.tn_grps(tnode)
                    grps = self.next.bgrid.tn_grps0(tn)
                    x = 1

                    self.chdic[gv] = tnode
        Center.add_path_tnodes(self.chdic)
        return self.next.spawn()

    def solve(self):
        Center.save_pathdic('path-fino1.json')

    def split_vkm(self):
        # pop-out touched-vk3s forming vk12dic with them
        # tdic: keyed by cvs of vks and values are lists of vks
        # make next-choice from vkm - if not empty, if it is empty, done=True
        self.vk12dic = {}  # store all vk12s, all tnode's vkdic ref to here
        tdic = {}
        for kn in self.choice['touched']:
            vk = self.vkm.pop_vk(kn)
            cvs, outdic = self.bgrid.cvs_and_outdic(vk)
            rvk = VKlause(vk.kname, outdic)
            for v in cvs:
                if v not in self.bgrid.covers:
                    s = tdic.setdefault(v, set([]))
                    s.add(rvk)
                if kn not in self.vk12dic:
                    self.vk12dic[kn] = rvk
        self.vk2grps = {}
        for v in self.bgrid.chheads:
            if v in tdic:
                d = self.vk2grps.setdefault(v, {})
                for vk2 in tdic[v]:
                    d[vk2.kname] = vk2

        if len(self.vkm.vkdic) == 0:
            self.done = True
            self.next_choice = None
        else:
            self.next_choice = self.vkm.choose_anchor()
            self.next = SatNode(
                self, self.next_sh.clone(), self.vkm, self.next_choice)
    # ---- def split_vkm(self) --------

    def is_top(self):
        return self.nov == Center.maxnov
