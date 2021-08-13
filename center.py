import json


class Center:
    maxnov = 0
    sats = []
    limit = 10

    repo = {}
    snodes = {}
    skeleton = {}
    topdowns = {}
    pathdic = {}

    @classmethod
    def add_vkm(cls, name, vkm):
        dic = cls.pathdic.setdefault(name, {})
        dic['all-vk'] = len(vkm.vkdic)
        dic['kn1s'] = vkm.kn1s
        dic['kn2s'] = vkm.kn2s

    @classmethod
    def add_path_tnodes(cls, pathdic):
        for key, v in pathdic.items():
            if type(v) == type({}):
                for name, tnode in v.items():
                    cls.add_vkm(name, tnode.vkm)

    @classmethod
    def add_paths(cls, pathdic):
        for key, vkm12 in pathdic.items():
            name = '-'.join(key)
            dic = cls.pathdic.setdefault(name, {})
            dic['all-vk'] = len(vkm12.vkdic)
            dic['kn1s'] = vkm12.kn1s
            dic['kn2s'] = vkm12.kn2s

    @classmethod
    def save_pathdic(cls, filename):
        if len(cls.pathdic) == 0:
            return
        pthkeys = sorted(cls.pathdic.keys())
        msg = ''
        for pkey in pthkeys:
            msg += '\n' + f'{pkey}:\n' + \
                json.dumps(cls.pathdic[pkey], indent=2, sort_keys=True)
        with open(filename, 'w') as ofile:
            ofile.write(msg)
