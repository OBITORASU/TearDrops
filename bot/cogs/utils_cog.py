import random
import discord
import wikipedia
import requests
import wolframalpha
from discord.ext import commands
from translate import Translator

def resolveListOrDict(variable):
    if isinstance(variable, list):
        return variable[0]['plaintext']
    else:
        return variable['plaintext']
def removeBrackets(variable):
    return variable.split('(')[0]

class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def echo(self, ctx, *args):
        '''echos the words'''
        output = ''
        for word in args:
            output += word
            output += ' '
        await ctx.send(output)

    @commands.command(pass_context=True)
    async def say(self, ctx, *args):
        """Gives the user's statement a nice richtext quote format"""
        output = ''
        for word in args:
            output += word
            output += ' '
        user = ctx.message.author
        embed = discord.Embed(
            title=f'{output}',
            description=f'~{user}',
            colour=discord.Color.greyple())
        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def urban(self, ctx, *args):
        '''searches urban dictionary for words'''
        baseurl = "https://www.urbandictionary.com/define.php?term="
        output = ''.join(args)
        await ctx.send(baseurl + output)

    @commands.command(pass_context=True)
    async def define(self, ctx, *args):
        '''searches merriam-webster for meanings of words'''
        baseurl = "https://www.merriam-webster.com/dictionary/"
        output = '%20'.join(args)
        await ctx.send(baseurl + output)


    @commands.command(pass_context=True)
    async def wiki(self, ctx, *, args):
        '''Displays wikipedia info about given arguments'''
        searchResults = wikipedia.search(args)
        if not searchResults:
            embed = discord.Embed(
                title=f'**{args}**',
                description='It appears that there is no instance of this in Wikipedia index...',
                colour=discord.Color.dark_red())
            embed.set_footer(text='Powered by Wikipedia...')
            await ctx.send(embed=embed)
        else:
            try:
                page = wikipedia.page(searchResults[0], auto_suggest=False)
                pg = 0
            except wikipedia.DisambiguationError as err:
                page = wikipedia.page(err.options[0], auto_suggest=False)
                pg = err.options
            wikiTitle = str(page.title.encode('utf-8'))
            wikiSummary = page.summary
            embed = discord.Embed(title=f'**{wikiTitle[1:]}**', description=str(
                wikiSummary[0:900]) + '...', color=discord.Color.dark_orange(), url=page.url)
            embed.set_footer(text='Powered by Wikipedia...')
            if pg != 0:
                s = pg[1:10] + ['...']
                s = ','.join(s)
                embed.add_field(name='Did you mean?:', value=s)
            embed.set_image(url=page.images[0])
            await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def wolfram(self, ctx, *args):
        '''displays info from wolfram'''
        ques = ''.join(args)
        wolfram = wolframalpha.Client("QYKRJ8-YT2JP8U85T")
        res = wolfram.query(ques)
        print(res)
        if res['@success'] == 'false':
            print('Question cannot be resolved')
        # Wolfram was able to resolve question
        else:
            result = ''
            # pod[0] is the question
            pod0 = res['pod'][0]
            # pod[1] may contains the answer
            pod1 = res['pod'][1]
            # checking if pod1 has primary=true or title=result|definition
            if (('definition' in pod1['@title'].lower()) or ('result' in  pod1['@title'].lower()) or (pod1.get('@primary','false') == 'true')):
                # extracting result from pod1
                result = resolveListOrDict(pod1['subpod'])
                await ctx.send(result)
            else:
                # extracting wolfram question interpretation from pod0
                question = resolveListOrDict(pod0['subpod'])
                # removing unnecessary parenthesis
                question = removeBrackets(question)
                # searching for response from wikipedia
                await wiki(self, ctx, question)

        await ctx.send(next(res.results).plainText)

    @commands.command(pass_context=True)
    async def weather(self, ctx, *, loc):
        '''displays weather data'''
        p = {"http": "http://111.233.225.166:1234"}
        k = "353ddfe27aa4b3537c47c975c70b58d9" # dummy key(for now)
        api_r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?appid={k}&q={loc}, verify= False, proxies=p")
        q = api_r.json()
        if q["cod"] != 404:
            weather_data={}
            temp = q['main']['temp']
            weather_data['Temperature'] = f'{str(round(temp-273.16, 2))} °C'

            p = q['main']['pressure']
            weather_data['Pressure'] = f'{str(p)} hpa'

            hum = q['main']['humidity']
            weather_data['Humidity'] = f'str{hum} %'

            wind = q['wind']['speed']
            weather_data['Wind Speed'] = wind

            w_obj = q['weather'][0]
            desc = w_obj['description']
            weather_data['\nDescription'] = desc
            w_id = str(w_obj['id'])
            if '8' in w_id[0]:
                if w_id=='800':
                    col=0xd8d1b4
                else:
                    col=0xbababa
            elif '7' in w_id[0]:
                col=0xc2eaea
            elif '6' in w_id[0]:
                col=0xdde5f4
            elif '5' in w_id[0]:
                col= 0x68707c
            elif '3' in w_id[0]:
                col= 0xb1c4d8
            elif '2' in w_id[0]:
                col= 0x4d5665
            else: col= 0x000000
            weather_data = [f'**{field}**: {weather_data[field]}' for field in weather_data]
            embed = discord.Embed(title='Weather',
                                  description=f'displaying weather of {loc}...',
                                  color=col)
            embed.add_field(name='\u200b',value='\n'.join(weather_data))
            embed.set_footer(text=f'Requested by {ctx.message.author.name}')
        else:
            embed = discord.Embed(title='Weather',
                                  description='API Connection Refused',
                                  color=discord.Color.red())
            embed.set_footer(text='Requested by {ctx.message.author.name}')

        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def translate(self, ctx, lang, *, args):
        '''Converts text to different language'''
        color = "%06x" % random.randint(0, 0xFFFFFF)

        translator = Translator(to_lang=f"{lang}", from_lang='autodetect')
        translated = translator.translate(f"{args}")
        embed = discord.Embed(title= "---translating--->",
                              description= f'{translated}\n~{ctx.message.author.mention}',
                              colour= int(color, 16))
        embed.set_footer(text=f'Translated to {lang}...')
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Utils(client))
