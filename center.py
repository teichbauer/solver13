import json


class Center:
    maxnov = 0
    satbits = set([])
    sats = []
    limit = 10

    repo = {}
    snodes = {}
    skeleton = {}
    topdowns = {}
    pathdic = {}

    @classmethod
    def get_vklist(cls, vkm, leng):
        lst = []
        if leng == 1:
            ks = sorted(vkm.kn1s)
        elif leng == 2:
            ks = sorted(vkm.kn2s)
        for k in ks:
            msg = f'{k}: ' + str(vkm.vkdic[k].dic)
            lst.append(msg)
        return lst

    @classmethod
    def add_vkm(cls, name, vkm):
        dic = cls.pathdic.setdefault(name, {})
        dic['all-vk'] = len(vkm.vkdic)
        dic['kn1s'] = cls.get_vklist(vkm, 1)
        dic['kn2s'] = cls.get_vklist(vkm, 2)

    @classmethod
    def add_path_tnodes(cls, pathdic):
        for key, v in pathdic.items():
            if type(v) == type({}):
                for name, tnode in v.items():
                    cls.add_vkm(name, tnode.vkm)

    @classmethod
    def filter_vk12(cls, vk, nov):
        if type(vk).__name__ == 'VKlause':
            while nov in cls.snodes:
                sn = cls.snodes[nov]
                for avk in sn.bgrid.avks:
                    if vk.hit(avk.dic):
                        return False
                nov -= 3
            return True
        elif type(vk) == type({}):
            for v in vk.values():
                if not cls.filter_vk12(v, nov):
                    return False
            return True

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
