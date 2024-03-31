class PlayerInventory:
    def __init__(self, weapons, items):
        self.__weapons = weapons
        self.__items = items

    def get_weapons(self):
        return self.__weapons

    def get_items(self):
        return self.__items


class Weapons:
    def __init__(self, ak47, m4, awp, mp5):
        self.__ak47 = ak47
        self.__m4 = m4
        self.__awp = awp
        self.__mp5 = mp5

    def get_ak47(self):
        return self.__ak47

    def get_m4(self):
        return self.__m4

    def get_awp(self):
        return self.__awp

    def get_mp5(self):
        return self.__mp5


class Items:
    def __init__(self, bandage, medkit):
        self.__bandage = bandage
        self.__medkit = medkit

    def get_bandage(self):
        return self.__bandage

    def get_medkit(self):
        return self.__medkit
