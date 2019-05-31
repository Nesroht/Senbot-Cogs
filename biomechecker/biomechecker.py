import discord
import json
import os
import copy
from pprint import pprint
from redbot.core import checks, Config, commands
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.data_manager import cog_data_path



class Biomechecker(commands.Cog):
    """Check various things in regards to Pixelmon BetterSpawner"""

    def __init__(self, bot):
        self.bot = bot
        self.pathbase = str(cog_data_path(self, "Biomechecker"))
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
        self.legendarySpecial = ["Articuno", "Zapdos", "Moltres", "Mewtwo", "Lugia", "HoOh", "Dialga", "Palkia", "Giratina", "Arceus", "Silvally", "Cosmoem", "Solgaleo", "Lunala", "Meltan", "Melmetal"]

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
        for i in self.legendarySpecial:
            self.legendaries["legendaries"].append(i)

        # with open('config/Change.json') as f:
        # change = json.load(f)

        for filename in os.listdir(self.pathbase + "/pixelmon"):
            if filename.endswith("set.json"):
                # log["log"].append(filename)
                with open(self.pathbase + "/pixelmon" + "/" + filename) as f:
                    self.data = json.load(f)
                if len(self.data["spawnInfos"]) <= 1:
                    if "stringBiomes" in self.data["spawnInfos"][0]["condition"]:
                        for location in self.data["spawnInfos"][0]["stringLocationTypes"]:
                            for biome in self.data["spawnInfos"][0]["condition"]["stringBiomes"]:
                                if biome in self.config["biomeCategories"]:
                                    # pprint(biome)
                                    for biomes in self.config["biomeCategories"][biome]:
                                        if ":" in biomes:
                                            dummp, biomes = biomes.split(":")
                                        if location in self.dataout:
                                            if biomes in self.dataout[location]:
                                                self.dataout[location].update(biome=self.dataout[location][biomes].append(self.data["id"]))
                                            else:
                                                self.dataout[location].update({biomes: [self.data["id"]]})
                                        else:
                                            # log["log"].append(biome + " - " + data["id"])
                                            self.dataout.update({location: {biomes: [self.data["id"]]}})
                                        if self.data["id"] in self.dataoutPixelmon:
                                            if location in self.dataoutPixelmon[self.data["id"]]:
                                                self.dataoutPixelmon[self.data["id"]][location].append(biomes)
                                            else:
                                                self.dataoutPixelmon[self.data["id"]].update({location: [biomes]})
                                        else:
                                            self.dataoutPixelmon.update({self.data["id"]: {location: [biomes]}})
                                else:
                                    if ":" in biome:
                                        dummp, biome = biome.split(":")
                                    if location in self.dataout:
                                        if biome in self.dataout[location]:
                                            self.dataout[location].update(biome=self.dataout[location][biome].append(self.data["id"]))
                                        else:
                                            self.dataout[location].update({biome: [self.data["id"]]})
                                    else:
                                        # log["log"].append(biome + " - " + data["id"])
                                        self.dataout.update({location: {biome: [self.data["id"]]}})
                                    if self.data["id"] in self.dataoutPixelmon:
                                        if location in self.dataoutPixelmon[self.data["id"]]:
                                            self.dataoutPixelmon[self.data["id"]][location].append(biome)
                                        else:
                                            self.dataoutPixelmon[self.data["id"]].update({location: [biome]})
                                    else:
                                        self.dataoutPixelmon.update({self.data["id"]: {location: [biome]}})
                    else:
                        pass
                else:
                    for test in self.data["spawnInfos"]:
                        if "stringBiomes" in test["condition"]:
                            for location in test["stringLocationTypes"]:
                                for biome in test["condition"]["stringBiomes"]:
                                    if biome in self.config["biomeCategories"]:
                                        # pprint(biome)
                                        for biomes in self.config["biomeCategories"][biome]:
                                            if ":" in biomes:
                                                dummp, biomes = biomes.split(":")
                                            if location in self.dataout:
                                                if biomes in self.dataout[location]:
                                                    self.dataout[location].update(biome=self.dataout[location][biomes].append(self.data["id"]))
                                                else:
                                                    # log["log"].append(biome + " - " + data["id"])
                                                    self.dataout[location].update({biomes: [self.data["id"]]})
                                            else:
                                                self.dataout.update({location:{biomes: [self.data["id"]]}})
                                            if self.data["id"] in self.dataoutPixelmon:
                                                if location in self.dataoutPixelmon[self.data["id"]]:
                                                    self.dataoutPixelmon[self.data["id"]][location].append(biomes)
                                                else:
                                                    self.dataoutPixelmon[self.data["id"]].update({location: [biomes]})
                                            else:
                                                self.dataoutPixelmon.update({self.data["id"]: {location: [biomes]}})
                                    else:
                                        if ":" in biome:
                                            dummp, biome = biome.split(":")
                                        if location in self.dataout:
                                            if biome in self.dataout[location]:
                                                self.dataout[location].update(
                                                    biome=self.dataout[location][biome].append(self.data["id"]))
                                            else:
                                                # log["log"].append(biome + " - " + data["id"])
                                                self.dataout[location].update({biome: [self.data["id"]]})
                                        else:
                                            self.dataout.update({location: {biome: [self.data["id"]]}})
                                        if self.data["id"] in self.dataoutPixelmon:
                                            if location in self.dataoutPixelmon[self.data["id"]]:
                                                self.dataoutPixelmon[self.data["id"]][location].append(biome)
                                            else:
                                                self.dataoutPixelmon[self.data["id"]].update({location: [biome]})
                                        else:
                                            self.dataoutPixelmon.update({self.data["id"]: {location: [biome]}})
                        elif len(test["stringLocationTypes"]) >= 1:
                            for location in test["stringLocationTypes"]:
                                if location in self.dataout:
                                    if location in self.dataout[location]:
                                        self.dataout[location].update(biome=self.dataout[location][location].append(self.data["id"]))
                                    else:
                                        self.dataout[location].update({location: [self.data["id"]]})
                                else:
                                    self.dataout.update({location: {location: [self.data["id"]]}})
                                if self.data["id"] in self.dataoutPixelmon:
                                    if location in self.dataoutPixelmon[self.data["id"]]:
                                        self.dataoutPixelmon[self.data["id"]][location].append(location)
                                    else:
                                        self.dataoutPixelmon[self.data["id"]].update({location: [location]})
                                else:
                                    self.dataoutPixelmon.update({self.data["id"]: {location: [location]}})
                        else:
                            pass



        with open(self.pathbase + '/Biomes.json', 'w') as out:
            out.write(json.dumps(self.dataout, indent=4, sort_keys=True))

        i = 1
        for pokemon in self.pokedex:
            if pokemon in self.dataoutPixelmon:
                list = self.dataoutPixelmon[pokemon]
                #print(self.dataoutPixelmon)
                if list:
                    for location in self.dataoutPixelmon[pokemon]:
                        #print(self.dataoutPixelmon[pokemon][0])
                        list2 = self.dataoutPixelmon[pokemon][location]
                        if list2:
                            self.dataoutPixelmonSorted.update({i:{pokemon:{location:list2}}})
                    i += 1
                else:
                    for location in self.dataoutPixelmon[pokemon]:
                        self.dataoutPixelmonSorted.update({i:{pokemon:{location:["Nowhere"]}}})
                    i += 1

        with open(self.pathbase + '/Pixelmon.json', 'w') as out:
            out.write(json.dumps(self.dataoutPixelmon, indent=4, sort_keys=True))

        with open(self.pathbase + '/PixelmonSorted.json', 'w') as out:
            out.write(json.dumps(self.dataoutPixelmonSorted, indent=4, sort_keys=True))

        with open(self.pathbase + '/commandlog.json', 'w') as logout:
            logout.write(json.dumps(self.log, indent=4, sort_keys=True))

        dataoutchecker = copy.deepcopy(self.dataout)
        for bi in self.ignore:
            for location in dataoutchecker:
                if bi in dataoutchecker[location]: del dataoutchecker[location][bi]

        for location in dataoutchecker:
            for biome in dataoutchecker[location]:
                list = dataoutchecker[location][biome]
                if list:
                    if len(list) <= 8:
                        self.amount.update({location:{biome: list}})
                else:
                    self.amount.update({location:{biome: ["None"]}})

        checker = copy.deepcopy(self.dataoutPixelmonSorted)
        for id in checker:
            for pixelmon in checker[id]:
                for location in checker[id][pixelmon]:
                    #pprint(str(id) + " - " + pixelmon + " - " + location)
                    list = checker[id][pixelmon][location]
                    if list:
                        for bi in self.ignore:
                            if bi in list: list.remove(bi)
                        if len(list) <= 5:
                            self.biomeamount.update({pixelmon:{location: list}})
                    else:
                        self.biomeamount.update({pixelmon:{location ["None"]}})

        with open(self.pathbase + '/TooFewPixelmon.json', 'w') as out:
            out.write(json.dumps(self.amount, indent=4, sort_keys=True))

        with open(self.pathbase + '/TooFewBiomes.json', 'w') as out:
            out.write(json.dumps(self.biomeamount, indent=4, sort_keys=True))

    @commands.command()
    async def rarity(self, ctx, pixelmon):
        """Returns the rarity of given pixelmon"""
        if pixelmon.title() in self.dataoutPixelmon:
            emb = discord.Embed(title="The rarity of " + pixelmon.title())
            strRare = ""
            with open(self.pathbase + '/pixelmon/'+pixelmon.title()+'.set.json') as f:
                self.data = json.load(f)
            for i in self.data["spawnInfos"]:
                strRare += "```\n" + str(i["rarity"]) + "\n```"
            emb.description = strRare
            await ctx.send(embed=emb)
        elif pixelmon in self.dataoutPixelmon:
            emb = discord.Embed(title="The rarity of " + pixelmon)
            strRare = ""
            with open(self.pathbase + '/pixelmon/'+pixelmon+'.set.json') as f:
                self.data = json.load(f)
            for i in self.data["spawnInfos"]:
                strRare += "```\n" + str(i["rarity"]) + "\n```"
            emb.description = "".join(strRare)
            await ctx.send(embed=emb)

    @commands.command()
    async def setrarity(self, ctx, pixelmon, rarity, index: int):
        """Sets the rarity of given pixelmon, requires index so check rarity first"""
        if pixelmon.title() in self.dataoutPixelmon:
            with open(self.pathbase + '/pixelmon/' + pixelmon.title() + '.set.json') as f:
                self.setrarityDump = json.load(f)
            self.setrarityDump["spawnInfos"][index]["rarity"] = float(rarity)
            with open(self.pathbase + '/pixelmon/' + pixelmon.title() + '.set.json', 'w') as out:
                out.write(json.dumps(self.setrarityDump, indent=4))
            emb = discord.Embed(title="The new rarity of " + pixelmon)
            strRare = ""
            for i in self.setrarityDump["spawnInfos"]:
                strRare += "```\n" + str(i["rarity"]) + "\n```"
            emb.description = "".join(strRare)
            await ctx.send(embed=emb)
            await ctx.send(file=discord.File(self.pathbase + '/pixelmon/' + pixelmon.title() + '.set.json'))
            self.setrarityDump = {}
        elif pixelmon in self.dataoutPixelmon:
            with open(self.pathbase + '/pixelmon/' + pixelmon + '.set.json') as f:
                self.setrarityDump = json.load(f)
            self.setrarityDump["spawnInfos"][index]["rarity"] = float(rarity)
            with open(self.pathbase + '/pixelmon/' + pixelmon + '.set.json', 'w') as out:
                out.write(json.dumps(self.setrarityDump, indent=4))
            emb = discord.Embed(title="The new rarity of " + pixelmon)
            strRare = ""
            for i in self.setrarityDump["spawnInfos"]:
                strRare += "```\n" + str(i["rarity"]) + "\n```"
            emb.description = "".join(strRare)
            await ctx.send(embed=emb)
            await ctx.send(file=discord.File(self.pathbase + '/pixelmon/' + pixelmon + '.set.json'))
            self.setrarityDump = {}

    @commands.command()
    async def legendaries(self, ctx):
        """Returns list of legendaries"""
        emb = discord.Embed(title="These Pixelmon are considered legendary")
        strLeg = []
        strLeg.append("```\n")
        for f in self.pokedex:
            if f in self.legendaries["legendaries"]:
                strLeg.append(f + "\n")
        strLeg.append("```")
        emb.description = "".join(strLeg)
        await ctx.send(embed=emb)


    @commands.command()
    async def toofewbiomes(self, ctx):
        """Returns a list of Pixelmon with less than 5 biomes they can spawn in"""
        limit = 5
        current = 0
        embeds = []
        noembed = True
        strBiomes = []
        if len(self.biomeamount) > 30:
            await ctx.send(embed=discord.Embed(title="Too many Pixelmon to list", description="There are too many Pixelmon with less than 5 biomes they can spawn in, so sending a .json file instead."))
            await ctx.send(file=discord.File(self.pathbase + '/' + 'TooFewBiomes.json'))
        else:
            for pixelmon in self.biomeamount:
                for location in self.biomeamount[pixelmon]:
                    if noembed:
                        emb = discord.Embed(title="These Pixelmon spawn in too few biomes.")
                        noembed = False
                        strBiomes = []
                    if current <= limit:
                        strBiomes.append("```\n")
                        for biome in self.biomeamount[pixelmon][location]:
                            strBiomes.append(location + " in " + biome + " \n")
                        if len(self.biomeamount[pixelmon]) == 0:
                            strBiomes.append("Nowhere \n")
                        strBiomes.append("```")
                        emb.add_field(name=pixelmon, value="".join(strBiomes), inline=False)
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
        """Returns a list of biomes with less than 8 possible pixelmon spawns"""
        limit = 5
        current = 0
        embeds = []
        noembed = True
        if len(self.amount) > 30:
            await ctx.send(embed=discord.Embed(title="Too many Biomes to list", description="There are too many biomes with less than 8 pixelmon that can spawn in them, so sending a .json file instead."))
            await ctx.send(file=discord.File(self.pathbase + '/' + 'TooFewBiomes.json'))
        else:
            for location in self.amount:
                for biomes in self.amount[location]:
                    if noembed:
                        emb = discord.Embed(title="These Biomes have too few pixelmon spawning")
                        noembed = False
                    if current <= limit:
                        strPixel = []
                        strPixel.append("```\n")
                        for pixelmon in self.amount[location][biomes]:
                            strPixel.append(pixelmon + " \n")
                        if len(self.amount[location][biomes]) == 0:
                            strPixel.append("None \n")
                        strPixel.append("```")
                        emb.add_field(name=location + " in " + biomes, value="".join(strPixel), inline=False)
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
        """Returns the biomes the given pixelmon can spawn in"""
        if pixelmon.title() in self.dataoutPixelmon:
            strBiomes = []
            strBiomes.append("```\n")
            limit = self.limit
            current = 0
            embeds = []
            for location in self.dataoutPixelmon[pixelmon.title()]:
                for biome in self.dataoutPixelmon[pixelmon.title()][location]:
                    if current <= limit:
                        strBiomes.append(location + " in " + biome + "\n")
                        current += 1
                    else:
                        emb = discord.Embed(title=pixelmon.title() + " spawns in the following locations.")
                        strBiomes.append("```")
                        emb.description = "".join(strBiomes)
                        embeds.append(emb)
                        current = 0
                        strBiomes = []
                        strBiomes.append("```\n")
            emb = discord.Embed(title=pixelmon.title() + " spawns in the following locations.")
            strBiomes.append("```")
            emb.description = "".join(strBiomes)
            embeds.append(emb)
            i = 1
            for embed in embeds:
                embed.set_footer(text="Page " + str(i) + "/" + str(len(embeds)))
                i += 1

            await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, page=0)
        elif pixelmon in self.dataoutPixelmon:
            strBiomes = []
            strBiomes.append("```\n")
            limit = self.limit
            current = 0
            embeds = []
            for location in self.dataoutPixelmon[pixelmon]:
                for biome in self.dataoutPixelmon[pixelmon][location]:
                    if current <= limit:
                        strBiomes.append(location + " in " + biome + "\n")
                        current += 1
                    else:
                        emb = discord.Embed(title=pixelmon + " spawns in the following locations.")
                        strBiomes.append("```")
                        emb.description = "".join(strBiomes)
                        embeds.append(emb)
                        current = 0
                        strBiomes = []
                        strBiomes.append("```\n")
            emb = discord.Embed(title=pixelmon + " spawns in the following locations.")
            strBiomes.append("```")
            emb.description = "".join(strBiomes)
            embeds.append(emb)
            i = 1
            for embed in embeds:
                embed.set_footer(text="Page " + str(i) + "/" + str(len(embeds)))
                i += 1

            await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, page=0)
        else:
            emb = discord.Embed(title=pixelmon.title() + " can't be found in the pokedex", description="Make sure you spell the name of the pokemon right, and that the pokemon exists")
            await ctx.send(embed=emb)

    @commands.command()
    async def pixelmonid(self, ctx, pixelmonid: int):
        """Returns the biomes the given pixelmon can spawn in, from #id"""
        if pixelmonid in self.dataoutPixelmonSorted:
            for pixelmon in self.dataoutPixelmonSorted[pixelmonid]:
                strBiomes = []
                strBiomes.append("```\n")
                climit = self.limit
                current = 0
                embeds = []
                for location in self.dataoutPixelmonSorted[pixelmonid][pixelmon]:
                    for biome in self.dataoutPixelmonSorted[pixelmonid][pixelmon][location]:
                        if current <= climit:
                            strBiomes.append(location + " in " + biome + "\n")
                            current += 1
                        else:
                            emb = discord.Embed(title=pixelmon + " spawns in the following locations.")
                            strBiomes.append("```")
                            emb.description = "".join(strBiomes)
                            embeds.append(emb)
                            current = 0
                            strBiomes = []
                            strBiomes.append("```\n")
                emb = discord.Embed(title=pixelmon + " spawns in the following locations.")
                strBiomes.append("```")
                emb.description = "".join(strBiomes)
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
        """Returns the pixelmon that can spawn in a specific biome, needs properly formatted biome name, so find it with [p]pixelmon first"""
        #pprint(self.dataout)
        for location in self.dataout:
            if biome in self.dataout[location]:
                strPixelmon = []
                limit = self.limit
                elimit = 3
                current = 0
                embeds = []
                noembed = True
                ecurrent = 0
                for pixelmon in self.dataout[location][biome]:
                    if noembed:
                        emb = discord.Embed(title=biome + " spawns the following Pixelmon in the following locations.")
                        strPixelmon.append("```\n")
                        noembed = False
                    if ecurrent < len(self.dataout[location]):
                        if current <= limit and current < len(self.dataout[location][biome]):
                            #print(pixelmon)
                            strPixelmon.append(pixelmon + "\n")
                            current += 1
                        else:
                            print("added to field")
                            strPixelmon.append("```")
                            emb.add_field(name=location, value="".join(strPixelmon))
                            strPixelmon = []
                            ecurrent += 1
                            current = 0
                    else:
                        embeds.append(emb)
                        current = 0
                        ecurrent = 0
                        noembed = True
                i = 1
                if noembed == False:
                    embeds.append(emb)
                for embed in embeds:
                    embed.set_footer(text="Page " + str(i) + "/" + str(len(embeds)))
                    i += 1
                await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, page=0)
            else:
                emb = discord.Embed(title=biome + " can't be found in the biome lists",
                                    description="Make sure you spell the name of the biome right, and that the biome exists")
                await ctx.send(embed=emb)
