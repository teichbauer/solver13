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
