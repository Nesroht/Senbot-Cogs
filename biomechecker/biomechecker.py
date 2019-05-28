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
        self.pathbase = str(cog_data_path(self, "Biomechecker"));
        self.dataout = {}
        self.limit = 20
        self.log = {'log': []}
        self.amount = {}
        self.biomeamount = {}
        self.config = {}
        self.dataoutPixelmon = {}
        self.dataoutPixelmonSorted = {}
        self.legendaries = {"legendaries": []}
        self.setrarityDump = {}
        self.poxedex = {}
        self.ignore = ["mushroom_island_shore", "grove", "mutated_cold_taiga", "hell", "visceral_heap", "undergarden", "sky",
                  "phantasmagoric_inferno", "origin_island", "corrupted_sands", "freezing_mountains", "arid_highland",
                  "polar_chasm", "fungi_forest"]

        with open(self.pathbase + '/config/BetterSpawnerConfig.json') as f:
            self.config = json.load(f)

        with open(self.pathbase + '/config/Pokedex.json') as f:
            self.pokedex = json.load(f)

        for filename in os.listdir(self.pathbase + "/legendaries"):
            if filename.endswith("set.json"):
                # log["log"].append(filename)
                with open(self.pathbase + "/legendaries" + "/" + filename) as f:
                    self.data = json.load(f)
                self.legendaries["legendaries"].append(self.data["id"])

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

        i = 1
        for pokemon in self.pokedex:
            if pokemon in self.dataoutPixelmon:
                list = self.dataoutPixelmon[pokemon]
                if list:
                    self.dataoutPixelmonSorted.update({i:{pokemon:list}})
                    i += 1
            else:
                self.dataoutPixelmonSorted.update({i:{pokemon:[]}})
                i += 1

        with open(self.pathbase + '/Pixelmon.json', 'w') as out:
            out.write(json.dumps(self.dataoutPixelmon, indent=4, sort_keys=True))

        with open(self.pathbase + '/PixelmonSorted.json', 'w') as out:
            out.write(json.dumps(self.dataoutPixelmonSorted, indent=4, sort_keys=True))

        with open(self.pathbase + '/commandlog.json', 'w') as logout:
            logout.write(json.dumps(self.log, indent=4, sort_keys=True))

        for bi in self.ignore:
            if bi in self.dataout: del self.dataout[bi]

        for biome in self.dataout:
            list = self.dataout[biome]
            if list:
                if len(list) <= 8:
                    self.amount.update({biome: list})

        for id in self.dataoutPixelmonSorted:
            for pixelmon in self.dataoutPixelmonSorted[id]:
                list = self.dataoutPixelmonSorted[id][pixelmon]
                if list:
                    for bi in self.ignore:
                        if bi in list: list.remove(bi)
                    if len(list) <= 5:
                        self.biomeamount.update({pixelmon: list})
                else:
                    self.biomeamount.update({pixelmon: ["None"]})

        with open(self.pathbase + '/TooFewPixelmon.json', 'w') as out:
            out.write(json.dumps(self.amount, indent=4, sort_keys=True))

        with open(self.pathbase + '/TooFewBiomes.json', 'w') as out:
            out.write(json.dumps(self.biomeamount, indent=4, sort_keys=True))

    @commands.command()
    async def rarity(self, ctx, pixelmon):
        emb = discord.Embed(title="The rarity of " + pixelmon)
        strRare = ""
        with open(self.pathbase + '/pixelmon/'+pixelmon.capitalize()+'.set.json') as f:
            self.data = json.load(f)
        for i in self.data["spawnInfos"]:
            strRare += "```" + str(i["rarity"]) + "\n```"
        emb.description = strRare
        await ctx.send(embed=emb)

    @commands.command()
    async def setrarity(self, ctx, pixelmon, rarity, index: int):
        with open(self.pathbase + '/pixelmon/' + pixelmon.capitalize() + '.set.json') as f:
            self.setrarityDump = json.load(f)
        self.setrarityDump["spawnInfos"][index]["rarity"] = float(rarity)
        with open(self.pathbase + '/pixelmon/' + pixelmon.capitalize() + '.set.json', 'w') as out:
            out.write(json.dumps(self.setrarityDump, indent=4))
        emb = discord.Embed(title="The new rarity of " + pixelmon)
        strRare = ""
        for i in self.setrarityDump["spawnInfos"]:
            strRare += "```" + str(i["rarity"]) + "\n```"
        emb.description = strRare
        await ctx.send(embed=emb)
        await ctx.send(file=discord.File(self.pathbase + '/pixelmon/' + pixelmon.capitalize() + '.set.json'))
        self.setrarityDump = {}

    @commands.command()
    async def legendaries(self, ctx):
        emb = discord.Embed(title="These Pixelmon are considered legendary")
        strLeg = "```"
        for i in self.legendaries["legendaries"]:
            strLeg += i + "\n"
        strLeg += "```"
        emb.description = strLeg
        await ctx.send(embed=emb)


    @commands.command()
    async def toofewbiomes(self, ctx):
        limit = 5
        current = 0
        embeds = []
        noembed = True
        for pixelmon in self.biomeamount:
            if noembed:
                emb = discord.Embed(title="These Pixelmon spawn in too few biomes.")
                noembed = False
            if current <= limit:
                strBiomes = "```"
                for biome in self.biomeamount[pixelmon]:
                    strBiomes += biome + " \n"
                if len(self.biomeamount[pixelmon]) == 0:
                    strBiomes += "None \n"
                strBiomes += "```"
                emb.add_field(name=pixelmon, value=strBiomes, inline=False)
                current += 1
            else:
                embeds.append(emb)
                current = 0
                noembed = True
        i = 1
        for embed in embeds:
            embed.set_footer(text="Page " + str(i) + "/" + str(len(embeds)))
            i += 1
        await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, page=0)

    @commands.command()
    async def toofewpixelmon(self, ctx):
        limit = 5
        current = 0
        embeds = []
        noembed = True
        for biomes in self.amount:
            if noembed:
                emb = discord.Embed(title="These Biomes have too few pixelmon spawning")
                noembed = False
            if current <= limit:
                strBiomes = "```"
                for biome in self.amount[biomes]:
                    strBiomes += biome + " \n"
                if len(self.amount[biomes]) == 0:
                    strBiomes += "None \n"
                strBiomes += "```"
                emb.add_field(name=biomes, value=strBiomes, inline=False)
                current += 1
            else:
                embeds.append(emb)
                current = 0
                noembed = True
        i = 1
        if noembed == False:
            embeds.append(emb)
        for embed in embeds:
            embed.set_footer(text="Page " + str(i) + "/" + str(len(embeds)))
            i += 1
        await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, page=0)

    @commands.command()
    async def pixelmon(self, ctx, pixelmon):
        if pixelmon.capitalize() in self.dataoutPixelmon:
            strBiomes = "```"
            limit = self.limit
            current = 0
            embeds = []
            for biome in self.dataoutPixelmon[pixelmon.capitalize()]:
                if current <= limit:
                    strBiomes += biome + "\n"
                    current += 1
                else:
                    emb = discord.Embed(title=pixelmon.capitalize() + " spawns in the following biomes.")
                    emb.description = strBiomes + "```"
                    #await ctx.send(embed=emb)
                    embeds.append(emb)
                    current = 0
                    strBiomes = "```"
            emb = discord.Embed(title=pixelmon.capitalize() + " spawns in the following biomes.")
            emb.description = strBiomes + "```"
            embeds.append(emb)
            i = 1
            for embed in embeds:
                embed.set_footer(text="Page " + str(i) + "/" + str(len(embeds)))
                i += 1

            await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, page=0)
        else:
            emb = discord.Embed(title=pixelmon.capitalize() + " can't be found in the pokedex", description="Make sure you spell the name of the pokemon right, and that the pokemon exists")
            await ctx.send(embed=emb)

    @commands.command()
    async def pixelmonid(self, ctx, pixelmonid: int):
        if pixelmonid in self.dataoutPixelmonSorted:
            for pixelmon in self.dataoutPixelmonSorted[pixelmonid]:
                strBiomes = "```"
                limit = self.limit
                current = 0
                embeds = []
                for biome in self.dataoutPixelmonSorted[pixelmonid][pixelmon]:
                    if current <= limit:
                        strBiomes += biome + "\n"
                        current += 1
                    else:
                        emb = discord.Embed(title=pixelmon + " spawns in the following biomes.")
                        emb.description = strBiomes + "```"
                        # await ctx.send(embed=emb)
                        embeds.append(emb)
                        current = 0
                        strBiomes = "```"
                emb = discord.Embed(title=pixelmon + " spawns in the following biomes.")
                emb.description = strBiomes + "```"
                embeds.append(emb)
                i = 1
                for embed in embeds:
                    embed.set_footer(text="Page " + str(i) + "/" + str(len(embeds)))
                    i += 1

                await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, page=0)
        else:
            emb = discord.Embed(title="Pokemon #" + pixelmonid + " can't be found in the pokedex",
                                description="Make sure the id of the pokemon exists.")
            await ctx.send(embed=emb)

    @commands.command()
    async def biomes(self, ctx, biome):
        if biome in self.dataout:
            strPixelmon = "```"
            limit = self.limit
            current = 0
            embeds = []
            for pixelmon in self.dataout[biome]:
                if current <= limit:
                    strPixelmon += pixelmon + "\n"
                    current += 1
                else:
                    emb = discord.Embed(title=biome + " spawns the following Pixelmon.")
                    emb.description = strPixelmon + "```"
                    embeds.append(emb)
                    current = 0
                    strPixelmon = "```"
            emb = discord.Embed(title=biome + " spawns the following Pixelmon.")
            emb.description = strPixelmon + "```"
            embeds.append(emb)
            i = 1
            for embed in embeds:
                embed.set_footer(text="Page " + str(i) + "/" + str(len(embeds)))
                i += 1

            await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, page=0)
        else:
            emb = discord.Embed(title=biome + " can't be found in the biome lists",
                                description="Make sure you spell the name of the biome right, and that the biome exists")
            await ctx.send(embed=emb)