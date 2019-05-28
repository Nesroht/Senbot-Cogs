import discord
import json
import os
from redbot.core import checks, Config, commands
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.data_manager import cog_data_path



class Biomechecker(commands.Cog):
    """Utility commands for Senbot"""

    def __init__(self, bot):
        self.bot = bot
        self.pathbase = str(cog_data_path(self, "Biomechecker")); self.dataout = {}
        self.log = {'log': []}
        self.amount = {}
        self.biomeamount = {}
        self.config = {}
        self.dataoutPixelmon = {}
        self.ignore = ["mushroom_island_shore", "grove", "mutated_cold_taiga", "hell", "visceral_heap", "undergarden", "sky",
                  "phantasmagoric_inferno", "origin_island", "corrupted_sands", "freezing_mountains", "arid_highland",
                  "polar_chasm", "fungi_forest"]

        with open(self.pathbase + '/config/BetterSpawnerConfig.json') as f:
            self.config = json.load(f)

        # with open('config/Change.json') as f:
        # change = json.load(f)

        for filename in os.listdir(self.pathbase + "/pixelmon"):
            if filename.endswith("set.json"):
                # log["log"].append(filename)
                with open(self.pathbase + "/pixelmon" + "/" + filename) as f:
                    self.data = json.load(f)
                if len(self.data["spawnInfos"]) <= 1:
                    if "stringBiomes" in self.data["spawnInfos"][0]["condition"]:
                        for biome in self.data["spawnInfos"][0]["condition"]["stringBiomes"]:
                            if biome in self.config["biomeCategories"]:
                                # pprint(biome)
                                for biomes in self.config["biomeCategories"][biome]:
                                    if ":" in biomes:
                                        dummp, biomes = biomes.split(":")
                                    if biomes in self.dataout:
                                        self.dataout.update(biome=self.dataout[biomes].append(self.data["id"]))
                                    else:
                                        # log["log"].append(biome + " - " + data["id"])
                                        self.dataout.update({biomes: [self.data["id"]]})
                                    if self.data["id"] in self.dataoutPixelmon:
                                        self.dataoutPixelmon.update(id=self.dataoutPixelmon[self.data["id"]].append(biomes))
                                    else:
                                        self.dataoutPixelmon.update({self.data["id"]: [biomes]})
                            else:
                                if ":" in biome:
                                    dummp, biome = biome.split(":")
                                if biome in self.dataout:
                                    self.dataout.update(biome=self.dataout[biome].append(self.data["id"]))
                                else:
                                    # log["log"].append(biome + " - " + data["id"])
                                    self.dataout.update({biome: [self.data["id"]]})
                                if self.data["id"] in self.dataoutPixelmon:
                                    self.dataoutPixelmon.update(id=self.dataoutPixelmon[self.data["id"]].append(biome))
                                else:
                                    self.dataoutPixelmon.update({self.data["id"]: [biome]})
                    else:
                        pass
                else:
                    for test in self.data["spawnInfos"]:
                        if "stringBiomes" in test["condition"]:
                            for biome in test["condition"]["stringBiomes"]:
                                if biome in self.config["biomeCategories"]:
                                    # pprint(biome)
                                    for biomes in self.config["biomeCategories"][biome]:
                                        if ":" in biomes:
                                            dummp, biomes = biomes.split(":")
                                        if biomes in self.dataout:
                                            self.dataout.update(biome=self.dataout[biomes].append(self.data["id"]))
                                        else:
                                            # log["log"].append(biome + " - " + data["id"])
                                            self.dataout.update({biomes: [self.data["id"]]})
                                        if self.data["id"] in self.dataoutPixelmon:
                                            self.dataoutPixelmon.update(id=self.dataoutPixelmon[self.data["id"]].append(biomes))
                                        else:
                                            self.dataoutPixelmon.update({self.data["id"]: [biomes]})
                                else:
                                    if ":" in biome:
                                        dummp, biome = biome.split(":")
                                    if biome in self.dataout:
                                        self.dataout.update(biome=self.dataout[biome].append(self.data["id"]))
                                    else:
                                        # log["log"].append(biome + " - " + data["id"])
                                        self.dataout.update({biome: [self.data["id"]]})
                                    if self.data["id"] in self.dataoutPixelmon:
                                        self.dataoutPixelmon.update(id=self.dataoutPixelmon[self.data["id"]].append(biome))
                                    else:
                                        self.dataoutPixelmon.update({self.data["id"]: [biome]})
                        else:
                            pass

        with open(self.pathbase + '/Biomes.json', 'w') as out:
            out.write(json.dumps(self.dataout, indent=4, sort_keys=True))

        with open(self.pathbase + '/Pixelmon.json', 'w') as out:
            out.write(json.dumps(self.dataoutPixelmon, indent=4, sort_keys=True))

        with open(self.pathbase + '/commandlog.json', 'w') as logout:
            logout.write(json.dumps(self.log, indent=4, sort_keys=True))

        for bi in self.ignore:
            if bi in self.dataout: del self.dataout[bi]

        for biome in self.dataout:
            list = self.dataout[biome]
            if list:
                if len(list) <= 8:
                    self.amount.update({biome: list})

        for pixelmon in self.dataoutPixelmon:
            list = self.dataoutPixelmon[pixelmon]
            if list:
                for bi in self.ignore:
                    if bi in list: list.remove(bi)
                if len(list) <= 5:
                    self.biomeamount.update({pixelmon: list})

        with open(self.pathbase + '/TooFewBiomes.json', 'w') as out:
            out.write(json.dumps(self.amount, indent=4, sort_keys=True))

        with open(self.pathbase + '/TooFewPixelmon.json', 'w') as out:
            out.write(json.dumps(self.biomeamount, indent=4, sort_keys=True))


    @commands.command()
    async def pixelmon(self, ctx, pixelmon):
        if pixelmon.capitalize() in self.dataoutPixelmon:
            strBiomes = "```"
            emb = discord.Embed(title=pixelmon.capitalize() + " spawns in the following biomes.")
            for biome in self.dataoutPixelmon[pixelmon.capitalize()]:
                strBiomes += biome + "\n"
            emb.description = strBiomes + "```"
            await ctx.send(embed=emb)
        else:
            emb = discord.Embed(title=pixelmon.capitalize() + " can't be found in the pokedex", description="Make sure you spell the name of the pokemon right, and that the pokemon exists")
            await ctx.send(embed=emb)

    @commands.command()
    async def biomes(self, ctx, biome):
        if biome in self.dataout:
            strPixelmon = "```"
            emb = discord.Embed(title=biome + " spawns in the following biomes.")
            for pixelmon in self.dataout[biome]:
                strPixelmon += pixelmon + "\n"
            emb.description = strPixelmon + "```"
            await ctx.send(embed=emb)
        else:
            emb = discord.Embed(title=biome + " can't be found in the biome lists",
                                description="Make sure you spell the name of the biome right, and that the biome exists")
            await ctx.send(embed=emb)