from worlds.AutoWorld import World
from BaseClasses import Item, Location, Region, ItemClassification
from . import client

GAME = "Pocket MuuMuu"

class PMItem(Item):
    game = GAME

class PMLocation(Location):
    game = GAME

class PocketMuuMuuWorld(World):
    game = GAME
    item_name_to_id = {"Money (1)": 7700001}
    location_name_to_id = {"Drop Zone - Star 1": 7700101}

    def create_item(self, name):
        return PMItem(name, ItemClassification.filler, self.item_name_to_id[name], self.player)

    def create_regions(self):
        menu = Region("Menu", self.player, self.multiworld)
        menu.locations.append(PMLocation(self.player, "Drop Zone - Star 1",
                                         self.location_name_to_id["Drop Zone - Star 1"], menu))
        self.multiworld.regions.append(menu)

    def create_items(self):
        self.multiworld.itempool.append(self.create_item("Money (1)"))

    def set_rules(self):
        self.multiworld.completion_condition[self.player] = lambda state: True