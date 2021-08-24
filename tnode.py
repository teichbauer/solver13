from vk12mgr import VK12Manager
from pathmgr import PathManager
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

    def approve(self, sn):  # next/lower snode, with its bitgrid
        # grid is bitgrid of next(lower snode)
        """for the grid of next(lower) level snode, do
        1.
        """
        gd = sn.bitgrid
        vkmdic = {}
        for k in gd.chheads:  # setup empty vk12ms for every ch-tnode
            vkmdic[k] = VK12Manager()
        # if any vk in self.vkm is hit by the grid/v, this v will be
        # put into dels, so that v/vkm pair be deleted from vkmdic
        for kn, vk in self.vkm.vkdic.items():
            cvs, vk12 = gd.cvs_and_outdic(vk)
            if cvs == None:  # vk12 didn't touch grid
                # add vk12 to every vkms
                # for v, vk12m in vkmdic.items():
                for v in gd.chheads:
                    if v in vkmdic:
                        vkmdic[v].add_vk(vk12)
                        if not vkmdic[v].valid:
                            del vkmdic[v]
                            break
            elif vk12 == None:  # vk is totally covered by grid.
                # cvs: list of values that are hit by vk
                for cv in cvs:
                    vkmdic.pop(cv, None)
            else:  # vk is partially hit by grid
                for cv in cvs:
                    if cv in vkmdic:
                        vkmdic[cv].add_vk(vk12)
                        if not vkmdic[cv].valid:
                            del vkmdic[cv]
        return {v: TNode(vkm, sn, v) for v, vkm in vkmdic.items()}

    def spawn(self, starting_vkm):
        pass

    def check_sat(self, sdic):
        vk12dic = {}
        for kn, vk in self.vkm.vkdic.items():
            total_hit, vk12 = vk.partial_hit_residue(sdic)
            if total_hit:
                return None
            elif vk12:
                vk12dic[kn] = vk12
        return vk12dic

    def find_path_vk12m(self, pnode_leftover_vk12dic):
        vk12m = self.vkm.clone()  # use a clone, don't touch self.vkm.vks
        # if not self.add_ancvks(vk12m):
        #     return None  # anc-vks make vk12m invalid -> negative return
        for kn, vk12 in pnode_leftover_vk12dic.items():
            vk12m.add_vk(vk12)
            if not vk12m.valid:
                return None
        return vk12m

    def filter_paths(self, pathmgr):
        # pathmgr is from higher-level snode.chdic[i].pthmgr
        total_hit = False
        pathdic = {}
        for pthname, vkm in pathmgr.dic.items():
            pvkm = self.vkm.clone()
            # if not self.add_ancvks(pvkm):
            #     continue
            for kn, vk in vkm.vkdic.items():
                total_hit, vk12 = vk.partial_hit_residue(self.hsat)
                if total_hit:
                    break  # -> go next pthname
                elif vk12:
                    pvkm.add_vk(vk12)
                    if not pvkm.valid:
                        break

            if (not total_hit) and pvkm.valid and len(pvkm.vkdic) > 0:
                pname = list(pthname)
                pname.insert(0, self.name)
                pathdic[tuple(pname)] = pvkm
        return pathdic
