import json
def S(o,u,p): return {"outlet":o,"url":u,"published":p}
def R(date,ships,flags,typ,where,zone,in_port,dist,lat,lon,cf,weapon,claimed,attr,sunk,cas,sources,**kw):
    d={"date_event":date,"ships":ships,"flags":flags,"type":typ,"where":where,"zone":zone,"in_port":in_port,
       "distance_nm":dist,"lat":lat,"lon":lon}
    if lat is not None: d["coords_from"]=cf
    d.update({"weapon":weapon,"claimed_by":claimed,"attributed_by":attr,"sunk":sunk,"casualties":cas,"sources":sources})
    if len({s["outlet"] for s in sources})<2: d["single_source"]=True
    d.update(kw); return d
F2T=lambda p="2026-10-09": S("Funnel2Tunnel tracker (aggregator)","https://funnel2tunnel.com/WestAsiaCrisis",p)
L=[]
# ---------------- JUNE
L.append(R("2026-06-05",["Natra","Zircon"],["Belize","Palau"],"bulk carrier / dry cargo","Taganrog Bay, Sea of Azov, en route Turkey->Rostov-on-Don in ballast","RU-coast",False,None,None,None,None,"aerial drone","none (Ukrainian military said the ships carried stolen grain/military cargo)","Azerbaijani media / The Insider: Ukrainian drones",False,"5 killed (Natra 2, Zircon 3); Zircon abandoned and burning",
 [S("AzerNews","https://www.azernews.az/nation/259364.html","2026-06-05"),S("Caliber.az","https://caliber.az/en/post/azerbaijani-sailors-killed-in-drone-strike-on-cargo-ships-in-sea-of-azov","2026-06-05"),S("The Insider","https://theins.press/en/news/297038","2026-09-10")]))
L.append(R("2026-06-10",["unnamed bulk carrier","unnamed bulk carrier"],["Panama","Barbados"],"bulk carrier","Ukrainian maritime corridor, Black Sea off Odesa region","UA-coast",False,None,None,None,None,"aerial drone","none","Ukraine (Odesa OVA, USPA): Russia",False,"none; fire extinguished, both continued",
 [S("RBC-Ukraine","https://newsukraine.rbc.ua/news/russian-drones-strike-two-vessels-in-black-1781118573.html","2026-06-10"),S("Odessa Journal","https://odessa-journal.com/public/2-merchant-ships-hit-by-russian-drone-attack-in-black-sea","2026-06-10")]))
L.append(R("2026-06-10",["WEST Horizon"],[],"chemical/oil tanker (sanctioned, 'shadow fleet')","Black Sea (location not given)","unknown",False,None,None,None,None,"unknown","Ukraine General Staff","none",False,"not reported; propulsion and steering disabled",
 [S("RBC-Ukraine","https://newsukraine.rbc.ua/news/ukrainian-forces-strike-shadow-fleet-tanker-1781088318.html","2026-06-10"),S("Wikipedia: Ukrainian attacks on the Russian shadow fleet","https://en.wikipedia.org/wiki/Ukrainian_attacks_on_the_Russian_shadow_fleet","2026-08-08")]))
L.append(R("2026-06-17",["Fina A"],[],"oil tanker (sanctioned, 'shadow fleet')","Black Sea (location not given)","unknown",False,None,None,None,None,"unknown","Ukraine General Staff","none",False,"not reported; damage being assessed",
 [S("Kyiv Independent","https://kyivindependent.com/ukraine-strikes-russian-shadow-fleet-tanker-in-black-sea-military-infrastructure-general-staff-says","2026-06-17")]))
L.append(R("2026-06-19",["unnamed cargo ship","unnamed cargo ship"],["Panama","St Kitts and Nevis"],"cargo","Black Sea, leaving Ukrainian (Odesa-region) ports","UA-coast",False,None,None,None,None,"aerial drone","none","Ukraine (Kuleba, Kiper): Russia",False,"1 killed, 2 injured (Panama ship); 3 lightly injured (St Kitts ship)",
 [S("Euromaidan Press","https://euromaidanpress.com/2026/06/19/russian-drones-kill-1-sailor-and-wound-five-in-attack-on-two-civilian-ships-in-the-black-sea","2026-06-19"),S("Kyiv Post","https://www.kyivpost.com/post/78534","2026-06-19"),S("Ports Europe","https://www.portseurope.com/russian-drones-hit-two-cargo-ships-near-ukraines-odesa-port","2026-06-19")],
 date_note="Ports Europe dates the strike to the night of 18 June"))
L.append(R("2026-06-22",["Victress","unnamed","unnamed"],["Panama","Palau","Belize"],"bulk/dry cargo","Black Sea, inbound to Ukrainian ports","UA-coast",False,None,None,None,None,"aerial drone","none","Ukraine (Navy, USPA, Kuleba): Russia",False,"1 killed (58-year-old Egyptian cook) on Victress, which lost seaworthiness; Palau and Belize ships damaged, continued",
 [S("Kyiv Post","https://www.kyivpost.com/post/78672","2026-06-22"),S("The Insider","https://theins.press/en/news/293981","2026-06-22")]))
# ---------------- JULY
L.append(R("2026-07-06",["(aggregate: Operation MoLoChKa, Sea of Azov, 118 vessels claimed by 18 Jul)"],[],"tankers, gas carriers, dry cargo, ferries, tugs, floating cranes","Sea of Azov","RU-coast",None,None,None,None,None,"aerial drone","Ukraine Unmanned Systems Forces (Brovdi)","none",None,"not itemised",
 [S("Kyiv Post","https://www.kyivpost.com/post/80156","2026-07-13"),S("USM","https://en.usm.media/overnight-the-uav-forces-hit-13-more-ships-of-the-shadow-fleet","2026-07-18"),S("Wikipedia: Operation MoLoChKa","https://en.wikipedia.org/wiki/Operation_MoLoChKa",None)],
 aggregate=True,count_claimed=118,period="2026-07-06/2026-07-14",note="Claimed counts, ships unnamed; Russia suspended Kerch Strait/Don-Azov navigation 10 Jul"))
L.append(R("2026-07-08",["Blue"],[],"oil tanker (sanctioned)","Black Sea, Ukraine's EEZ","open-sea",False,None,None,None,None,"sea drone","SBU (Sea Baby)","none",False,"not reported",
 [S("Ukrainian News","https://ukranews.com/en/news/1163396-ssu-maritime-drones-attack-russian-shadow-fleet-tankers-louise-1-and-banda-in-black-sea","2026-07-16"),S("Caliber.az","https://caliber.az/en/post/ukraine-says-sea-drones-struck-russian-shadow-fleet-oil-tankers-in-black-sea","2026-07-16")],
 date_note="approximate: reported as 'last week' on 16 Jul"))
L.append(R("2026-07-13",["unnamed cargo ship"],["Togo"],"cargo (unloading fertiliser)","port in Odesa region","UA-port",True,None,None,None,None,"unknown","none","Ukraine (Kuleba, USPA): Russia",False,"3 killed, 5 injured",
 [S("Glavnoe","https://glavnoe.in.ua/en/news-en/russia-strikes-civilian-vessel-under-foreign-flag-in-odesa-region-killing-three-sailors","2026-07-13"),S("United24 Media","https://united24media.com/war-in-ukraine/russian-strike-on-foreign-commercial-ship-in-odesa-kills-three-sailors-20713","2026-07-13")]))
L.append(R("2026-07-14",["unnamed","unnamed"],["Tanzania","Liberia"],"cargo","maritime corridor, Black Sea off Odesa region","UA-coast",False,None,None,None,None,"unknown","none","Ukraine (Kiper): Russia",False,"captain of one ship killed, 3 injured; 11 crew evacuated",
 [S("Kyiv Post","https://www.kyivpost.com/post/80264","2026-07-14"),S("United24 Media","https://united24media.com/war-in-ukraine/russia-attacks-two-civilian-cargo-ships-in-black-sea-killing-captain-and-injuring-three-20779","2026-07-14")]))
L.append(R("2026-07-14",["unnamed cargo ship"],["Marshall Islands"],"cargo","port in Odesa region","UA-port",True,None,None,None,None,"aerial drone","none","Ukraine (Kiper): Russia",False,"2 killed; superstructure fire",
 [S("Kyiv Independent","https://kyivindependent.com/second-russian-strike-on-foreign-vessel-within-days-kills-2-in-odesa-oblast","2026-07-15"),S("Kyiv Post","https://www.kyivpost.com/post/80264","2026-07-14"),S("United24 Media","https://united24media.com/war-in-ukraine/russian-strike-on-civilian-marshall-islands-flagged-cargo-ship-kills-two-in-odesa-region-20789","2026-07-15")]))
L.append(R("2026-07-15",["(Russian MoD claim: four vessels)"],[],"cargo","ports of Chornomorsk and Dnipro-Buh","UA-port",True,None,None,None,None,"unknown","Russian Defence Ministry","none",False,"not reported",
 [S("The Moscow Times (Reuters)","https://www.themoscowtimes.com/2026/07/15/russian-attack-on-odesa-kills-3-as-ukraine-strikes-ships-in-black-sea-a93251","2026-07-15"),S("Al Jazeera","https://www.aljazeera.com/news/2026/7/15/russian-attack-on-odesa-kills-three-as-ukraine-targets-vessels-in-black-sea","2026-07-15")],
 claim_only=True,note="Claim; may overlap with 13-14 Jul Ukrainian-reported incidents"))
L.append(R("2026-07-15",["(aggregate: MoLoChKa Black Sea phase, 20 vessels first night: 17 oil tankers, 2 LNG tankers, 1 tug; 54 Black Sea vessels by 18 Jul; 215 vessels in July overall)"],[],"tankers, gas carriers, dry cargo, tugs, floating cranes","Black Sea (Russian-linked shipping)","unknown",None,None,None,None,None,"aerial drone","Ukraine Unmanned Systems Forces (Brovdi)","none",None,"not itemised",
 [S("United24 Media","https://united24media.com/war-in-ukraine/after-the-sea-of-azov-ukraines-drone-fleet-turns-to-the-black-sea-hitting-20-russian-ships-20788","2026-07-15"),S("USM","https://en.usm.media/overnight-the-uav-forces-hit-13-more-ships-of-the-shadow-fleet","2026-07-18"),S("Reuters","https://www.reuters.com/business/aerospace-defense/russia-says-it-hits-military-targets-kyiv-ukrainian-ports-2026-07-16","2026-07-16")],
 aggregate=True,count_claimed=54,period="2026-07-15/2026-07-31",note="Claimed counts, unverified; named July hits on Russian-linked ships are listed separately and may be inside this count"))
L.append(R("2026-07-15",["unnamed tanker"],["Liberia"],"tanker","drifting awaiting berth at Novorossiysk","RU-coast",False,None,42.883,37.183,"source","aerial drone","none","none",False,"none; hull damage, engine room partially flooded, tow arranged",
 [F2T()],note="UKMTO-style report quoted by aggregator"))
L.append(R("2026-07-15",["unnamed tanker"],[],"tanker","at anchor, 45°02.5'N 036°39'E (Kerch Strait approaches)","RU-coast",False,None,45.042,36.65,"source","aerial drone","none","none",False,"3 minor injuries",
 [F2T()],note="UKMTO-style report quoted by aggregator"))
L.append(R("2026-07-15",["Louise 1","Banda"],[],"oil tanker (sanctioned)","off Russian Black Sea coast, footage suggests off Novorossiysk / Sochi","RU-coast",False,None,None,None,None,"sea drone","SBU (Mamai naval drones) with Ukrainian Navy","none",False,"not reported",
 [S("Kyiv Post","https://www.kyivpost.com/post/80381","2026-07-16"),S("Interfax-Ukraine","https://en.interfax.com.ua/news/general/1185375.html","2026-07-16")],
 date_note="SBU gave no date; announced 15-16 Jul"))
L.append(R("2026-07-17",["unnamed bulk carrier (laid up since 2022)"],[],"bulk carrier","moored at Olvia seaport (Mykolaiv region)","UA-port",True,None,46.64,31.72,"place-approx","aerial drone","none","none",False,"2 crew killed",
 [F2T()],note="UKMTO-style report quoted by aggregator"))
L.append(R("2026-07-17",["two unnamed bulk carriers (laid up since 2022)"],[],"bulk carrier","Mykolaiv Sea Port and a Mykolaiv shipyard","UA-port",True,None,46.97,32.0,"place-approx","aerial drone","none","none",False,"none reported",
 [F2T()],note="Two separate UKMTO-style reports quoted by aggregator"))
L.append(R("2026-07-17",["unnamed cargo ship"],["Marshall Islands"],"cargo","Odesa port","UA-port",True,None,None,None,None,"missile","none","Ukraine (Kiper): Russia",False,"4 injured of 17 crew",
 [S("Kyiv Post","https://www.kyivpost.com/post/80577","2026-07-18")]))
L.append(R("2026-07-17",["Avero"],[],"Suezmax oil tanker (sanctioned)","Black Sea, ~600 km from Ukrainian border","unknown",False,None,None,None,None,"sea drone","SBU (Mamai)","none",False,"not reported",
 [S("Ground News summary","https://ground.news/article/2-russian-shadow-fleet-tankers-hit-by-drones-in-black-sea-sbu-says","2026-07-18")],date_note="approximate"))
L.append(R("2026-07-18",["Venturo"],["Antigua and Barbuda"],"bulk carrier (supramax)","off Odesa coast / Odesa-region port infrastructure","UA-coast",False,None,None,None,None,"unknown","none","Ukraine (Kiper): Russia",False,"1 killed (Filipino), 3 injured; 17 evacuated; lost propulsion",
 [S("Kyiv Post","https://www.kyivpost.com/post/80577","2026-07-18"),S("Antigua News Herald","https://antiguanherald.com/articles/2026/07/20/antigua-flagged-ship-hit-in-russian-strike-on-odesa-one-seafarer-dead.html","2026-07-20")]))
L.append(R("2026-07-18",["Omorfi"],["Marshall Islands"],"cargo","Black Sea, reportedly in Russian territorial waters","RU-coast",False,None,None,None,None,"unknown","none","none",False,"1 Indian crew killed",
 [F2T()]))
L.append(R("2026-07-18",["unnamed oil tanker"],[],"oil tanker","transiting at 42°20'N 032°44'E (north of Turkish coast)","TR-EEZ",False,None,42.333,32.733,"source","sea drone","none","none",False,"none",
 [F2T()],note="UKMTO-style report quoted by aggregator; zone inferred from coordinates"))
L.append(R("2026-07-18",["unnamed bulk carrier"],[],"bulk carrier","transiting at 44°44.9'N 036°32.6'E","RU-coast",False,None,44.748,36.543,"source","aerial drone","none","none",False,"none",
 [F2T()],note="UKMTO-style report quoted by aggregator"))
L.append(R("2026-07-19",["unnamed bulk carrier"],[],"bulk carrier","transiting at 44°48'N 036°34'E en route to Russia","RU-coast",False,None,44.8,36.567,"source","aerial drone","none","none",False,"2 minor injuries",
 [F2T()],note="Close to the 18 Jul position; possibly a different vessel, not merged"))
L.append(R("2026-07-19",["Golden Leo"],["Guinea-Bissau"],"bulk/general cargo (corn)","leaving Odesa-region port; sank ~5 nm off Odesa on 26 Jul","UA-coast",False,5,None,None,None,"missile","none","Ukraine (USPA): Russia (3 cruise missiles)",True,"10 killed incl. Ukrainian pilot (USPA); other reports 4-5; 8 survivors",
 [S("United24 Media","https://united24media.com/war-in-ukraine/russia-targets-civilian-corn-export-vessel-near-odesa-leaving-10-dead-20895","2026-07-20"),S("The Guardian","https://www.theguardian.com/world/live/2026/jul/20/ukraine-russia-drones-missiles-hungary-germany-latest-news-updates","2026-07-20")],
 note="sank 2026-07-26; casualty count differs between sources"))
L.append(R("2026-07-19",["Asia","Nissos Ios"],["Liberia","Marshall Islands"],"oil tanker","CPC terminal, Novorossiysk","RU-port",True,None,None,None,None,"aerial drone","none","Ukrainian drones (per aggregator)",False,"not reported",
 [F2T()]))
L.append(R("2026-07-20",["Nelsa"],["Cameroon"],"oil tanker","loading at CPC terminal near Novorossiysk","RU-port",True,None,None,None,None,"aerial drone","none","none",False,"none; 22 evacuated, fire extinguished",
 [S("Seatrade Maritime","https://www.seatrade-maritime.com/security/ukraine-and-russia-strike-multiple-in-the-black-sea","2026-07-22"),F2T()]))
L.append(R("2026-07-21",["Gas Lisbon"],["Liberia"],"LPG tanker","~20 nm off Sfantu Gheorghe, Romania, bound for Reni","RO-EEZ",False,20,44.75,29.95,"place-approx","aerial drone","none","none",False,"3 injured; 1 later died of burns (aggregator)",
 [S("Turkiye Today","https://www.turkiyetoday.com/world/ukraine-bound-gas-tanker-struck-off-romania-as-black-sea-attacks-on-shipping-mount-3224329","2026-07-22"),F2T()]))
L.append(R("2026-07-22",["Reyhan Sari"],["Turkey"],"general cargo (coal, Taman->Trabzon)","off Novorossiysk","RU-coast",False,None,None,None,None,"aerial drone","none","none (no link established to Ukrainian op)",False,"1 killed, 3 wounded",
 [S("Turkiye Today","https://www.turkiyetoday.com/world/turkish-sailor-killed-in-drone-strike-on-black-sea-coal-ship-3224446","2026-07-23"),S("New Indian Express (AFP)","https://www.newindianexpress.com/world/2026/Sep/23/black-sea-drone-attacks-spell-terror-for-turkish-sailors","2026-09-23")]))
L.append(R("2026-07-22",["Golden Rose"],[],"bulk carrier","Black Sea (Ukrainian rescue zone)","UA-coast",False,None,None,None,None,"aerial drone","none","Ukraine (State Border Guard Service): Russia",False,"none; 16 evacuated",
 [S("UA.News (citing DPSU)","https://ua.news/en/ukraine/prikordonniki-vriatuvali-ekipazh-sudna-urazhenogo-rosiiskim-dronom-u-chornomu-mori","2026-07-22")]))
L.append(R("2026-07-22",["(Russian MoD claim: dry-cargo ship at Chornomorsk; dry-cargo ship and bulk carrier bound for Odesa; later 'four cargo ships and a bulk carrier')"],[],"cargo / bulk","Chornomorsk port and Black Sea approaches to Odesa","UA-port",True,None,None,None,None,"unknown","Russian Defence Ministry","none",False,"not reported",
 [S("The Moscow Times (Reuters)","https://www.themoscowtimes.com/2026/07/22/russia-says-it-struck-ukrainian-ports-and-ships-a93312","2026-07-22"),S("SAFETY4SEA","https://safety4sea.com/black-sea-shipping-crisis-deepens-as-attacks-intensify","2026-07-23")],claim_only=True))
L.append(R("2026-07-23",["Christiana B"],["Liberia"],"bulk carrier (coal to Ukraine)","~22 nm SE of Sfantu Gheorghe, Romanian EEZ","RO-EEZ",False,22,44.63,29.93,"place-approx","unknown","none","Romanian authorities: sea drone or naval mine",False,"none",
 [F2T()],note="Aggregator quotes Romanian DSU/MRCC; weapon mine or drone"))
L.append(R("2026-07-25",["AGN Ragnar"],["Palau"],"general cargo","Odesa port","UA-port",True,None,None,None,None,"aerial drone","none","Ukraine / Indian embassy reporting: Russia",False,"2 of 4 Indian crew unaccounted for at time of report; crew and pilot evacuated",
 [S("Dynamite News","https://www.dynamitenews.com/international/odesa-port-attack-what-happened-to-vessel-carrying-four-indians-2nd-attack-within-a-week","2026-07-26"),S("OSINT613","https://www.osint613.com/post/russian-drone-hits-cargo-ship-near-odesa-18515",None)]))
L.append(R("2026-07-26",["unnamed commercial vessel"],[],"unknown","southern Black Sea","unknown",False,None,None,None,None,"unknown","none","none",False,"none reported; damage",
 [F2T()],note="UKMTO-documented per aggregator"))
L.append(R("2026-07-28",["unnamed vessel (anchored, no crew or cargo)"],["Liberia"],"unknown","anchored in Black Sea off Odesa region","UA-coast",False,None,None,None,None,"unknown","none","Ukraine: Russia",False,"none (no crew aboard); third strike on this vessel",
 [F2T()]))
L.append(R("2026-07-30",["Nissos Sifnos","Marathi"],["Marshall Islands"],"crude oil tanker","CPC terminal SPM-3 near Novorossiysk; Marathi ~6 nm away","RU-port",True,None,None,None,None,"aerial drone","none","CPC: 'terrorist attack' (no attribution)",False,"none; fire extinguished",
 [S("TASS","https://tass.com/emergencies/2167129","2026-07-30"),F2T()]))
# ---------------- AUGUST
L.append(R("2026-08-01",["Yanina"],["Russia"],"container ship (FESCO/Rosatom)","eastern Black Sea near Novorossiysk","RU-coast",False,None,None,None,None,"sea drone","none","Rosatom: Ukrainian drones",True,"none; 17 crew rescued",
 [S("The Moscow Times (AFP)","https://www.themoscowtimes.com/2026/08/01/ukraine-sinks-russian-owned-container-ship-in-black-sea-rosatom-says-a93393","2026-08-01"),S("RBC-Ukraine","https://newsukraine.rbc.ua/news/drones-strike-cargo-ship-near-russia-s-novorossiysk-1785846301.html","2026-08-04")]))
L.append(R("2026-08-03",["Nadezhda"],["Cameroon"],"ro-ro cargo (Turkish-owned)","~20 nm off Novorossiysk, en route to Samsun","RU-coast",False,20,44.45,37.55,"place-approx","aerial drone","none","none",False,"3 seriously injured; 22 evacuated",
 [S("RBC-Ukraine (citing Reuters)","https://newsukraine.rbc.ua/news/drones-strike-cargo-ship-near-russia-s-novorossiysk-1785846301.html","2026-08-04"),S("The Insider","https://theins.press/en/news/297038","2026-09-10")]))
L.append(R("2026-08-03",["Yasar"],[],"cargo (Turkish-linked)","after departing Novorossiysk","RU-coast",False,None,None,None,None,"aerial drone","none","none",False,"not reported",
 [S("The Insider","https://theins.press/en/news/297038","2026-09-10")],date_note="approximate; mentioned with Nadezhda; aggregator lists a Turkish cargo ship attack on 3-4 Aug"))
L.append(R("2026-08-05",["Emil"],["Liberia"],"bulk carrier (German-owned, capesize)","~21 nm from Odesa","UA-coast",False,21,46.2,30.95,"place-approx","aerial drone","Russian Defence Ministry (claimed two cargo ships carrying military goods)","Ukraine: Russia",False,"none; 11 crew evacuated",
 [S("Euronews","https://www.euronews.com/my-europe/2026/08/06/russian-drones-attack-german-cargo-ship-emil-in-black-sea-media-reports","2026-08-06"),F2T()]))
L.append(R("2026-08-05",["Mera Queen"],["Guinea-Bissau"],"grain carrier (wheat)","Black Sea off Odesa region","UA-coast",False,None,None,None,None,"aerial drone","Russian Defence Ministry (claimed)","Ukraine: Russia",False,"1 killed, 3 injured",
 [S("Euronews (citing Bild)","https://www.euronews.com/my-europe/2026/08/06/russian-drones-attack-german-cargo-ship-emil-in-black-sea-media-reports","2026-08-06"),F2T()]))
L.append(R("2026-08-07",["unidentified 141 m Russian cargo vessel"],["Russia"],"cargo","near Novorossiysk","RU-coast",False,None,None,None,None,"unknown","none","aggregator: assessed Ukrainian drone strike",True,"not reported",
 [F2T()],note="Low confidence"))
L.append(R("2026-08-12",["unnamed cargo vessel"],["Guinea-Bissau"],"cargo","Odesa port","UA-port",True,None,None,None,None,"aerial drone","none","Ukraine: Russia",False,"1 injured",
 [F2T()]))
L.append(R("2026-08-16",["Skiros"],["Liberia"],"Suezmax tanker","Black Sea near Novorossiysk after loading at CPC","RU-coast",False,None,None,None,None,"aerial drone","none","suspected Ukrainian drone",False,"none reported; bridge fire",
 [F2T()]))
L.append(R("2026-08-17",["Anna S"],["Liberia"],"bulk carrier (Greek-owned, empty, to load grain)","~20 nm off Novorossiysk","RU-coast",False,20,44.45,37.5,"place-approx","aerial drone","none","none",False,"none; 21 crew abandoned ship, vessel almost destroyed",
 [S("SAFETY4SEA (citing Bloomberg)","https://safety4sea.com/at-least-five-vessels-carrying-grain-attacked-in-novorossiysk-and-tuapse","2026-08-19"),F2T()]))
L.append(R("2026-08-17",["Elina B"],["Malta"],"bulk carrier (56,000 t wheat)","near Novorossiysk, ~5 h after Anna S","RU-coast",False,None,None,None,None,"aerial drone","none","none",False,"none; continued to Bosphorus",
 [S("SAFETY4SEA (citing Bloomberg)","https://safety4sea.com/at-least-five-vessels-carrying-grain-attacked-in-novorossiysk-and-tuapse","2026-08-19"),F2T()]))
L.append(R("2026-08-18",["Victoria V","Fehu"],["Russia","Marshall Islands"],"bulk carrier (grain)","near Novorossiysk","RU-coast",False,None,None,None,None,"aerial drone","none","none",False,"not reported",
 [S("SAFETY4SEA (citing Bloomberg)","https://safety4sea.com/at-least-five-vessels-carrying-grain-attacked-in-novorossiysk-and-tuapse","2026-08-19"),F2T()]))
L.append(R("2026-08-18",["Necibe"],["San Marino"],"bulk/general cargo (to load wheat)","port of Tuapse (Turkiye Today: near Novorossiysk)","RU-port",True,None,None,None,None,"aerial drone","none","none",False,"crew evacuated to RoRo Ural",
 [S("SAFETY4SEA (citing Bloomberg)","https://safety4sea.com/at-least-five-vessels-carrying-grain-attacked-in-novorossiysk-and-tuapse","2026-08-19"),S("Turkiye Today","https://www.turkiyetoday.com/nation/turkish-cook-killed-after-drone-strikes-rescue-ship-that-had-saved-him-from-earlier-a-3226612","2026-08-22")],
 note="Location conflict between sources; date 17-18 Aug"))
L.append(R("2026-08-21",["Ural"],["Cameroon"],"ro-ro (Turkish-owned)","off Novorossiysk, carrying rescued Necibe crew","RU-coast",False,None,None,None,None,"aerial drone","none","none",False,"1 killed (Turkish cook from Necibe), 8 injured",
 [S("Turkiye Today","https://www.turkiyetoday.com/nation/turkish-cook-killed-after-drone-strikes-rescue-ship-that-had-saved-him-from-earlier-a-3226612","2026-08-22")],date_note="approximate (between 18 and 22 Aug)"))
L.append(R("2026-08-22",["RMS Team"],[],"general cargo (Turkish-operated)","Black Sea en route Gemlik->Novorossiysk","unknown",False,None,None,None,None,"aerial drone","none","none",False,"1 missing, 11 rescued; likely beyond economical repair",
 [F2T(),S("DataPortuaria","https://dataportuaria.com/en/internacional/shipping/rms-team-arrives-in-samsun-after-drone-attack-in-black-sea","2026-09-28")]))
L.append(R("2026-08-24",["unnamed MSC container vessel"],[],"container ship","Novorossiysk","RU-port",None,None,None,None,None,"unknown","none","none",False,"not reported",
 [S("RT (citing Bloomberg)","https://www.rt.com/news/644704-turkish-cargo-ship-drones","2026-08-27"),S("Ukrainska Pravda","https://www.pravda.com.ua/eng/news/2026/09/09/8052530/","2026-09-09")],
 date_note="unknown exact date, 'earlier this week' before 27 Aug",note="MSC suspended Novorossiysk bookings after the damage"))
L.append(R("2026-08-26",["Lider Bordo Mavi"],["Cameroon"],"ro-ro / container (vegetables, Samsun->Tuapse)","off Tuapse","RU-coast",False,None,None,None,None,"aerial drone","none","Turkish media: suspected Ukrainian campaign",False,"5 injured",
 [S("ShipFinder","https://www.shipfinder.com/maritime-news/maritime-security/drone-strike-tuapse-black-sea-2026-08-26","2026-08-28"),S("RT","https://www.rt.com/news/644704-turkish-cargo-ship-drones","2026-08-27"),S("DataPortuaria","https://dataportuaria.com/en/internacional/current-affairs/lider-bordo-mavi-struck-by-drones-off-tuapse-five-crew-injur",None)]))
L.append(R("2026-08-01",["(aggregate: MoLoChKa, 54 vessels claimed in August)"],[],"mixed","Black Sea and Sea of Azov","unknown",None,None,None,None,None,"aerial drone","Ukraine Unmanned Systems Forces (Brovdi)","none",None,"not itemised",
 [S("Militarnyi","https://militarnyi.com/en/news/ukraine-drone-avoid-helicopter-hit-tanker/","2026-09-12"),S("United24 via Ukraine Today","https://ukrainetoday.org/ukrainian-drone-evades-russian-helicopter-fire-and-strikes-sanctioned-oil-tanker-near-sochi","2026-09-12")],
 aggregate=True,count_claimed=54,period="2026-08-01/2026-08-31"))
# ---------------- SEPTEMBER
L.append(R("2026-09-01",["(aggregate: MoLoChKa, 16 vessels claimed 1-11 Sep; >300 total by 22 Sep)"],[],"mixed","Black Sea and Sea of Azov","unknown",None,None,None,None,None,"aerial drone","Ukraine Unmanned Systems Forces (Brovdi)","none",None,"not itemised",
 [S("Militarnyi","https://militarnyi.com/en/news/ukraine-drone-avoid-helicopter-hit-tanker/","2026-09-12"),S("Tech Times","https://www.techtimes.com/articles/328739/20261007/ukrainian-sea-drones-set-sochi-ablaze-hitting-russia-where-sanctions-failed.htm","2026-10-07")],
 aggregate=True,count_claimed=16,period="2026-09-01/2026-09-11"))
L.append(R("2026-09-09",["Tedy"],["Somalia"],"tug (escorting ships to Odesa)","near Odesa port; hit again while heading to Constanta","UA-coast",False,None,None,None,None,"aerial drone","Russian Defence Ministry (claimed striking a tug escorting ships into Odesa)","Azerbaijani sailors' association / Ukraine: Russia",False,"2 killed (Azerbaijani), 2+ burned (Kyiv Post: 8 wounded)",
 [S("The Insider","https://theins.press/en/news/297038","2026-09-10"),S("Kyiv Post","https://www.kyivpost.com/post/86032","2026-10-03"),S("Euronews","https://www.euronews.com/2026/09/11/two-azerbaijani-sailors-killed-in-black-sea-tugboat-drone-attack","2026-09-11")]))
L.append(R("2026-09-12",["Armada Leader"],["Russia"],"oil products tanker (sanctioned, IMO 9260483)","near Sochi","RU-coast",False,None,None,None,None,"aerial drone","Ukraine Unmanned Systems Forces (Brovdi)","none",False,"not reported",
 [S("Militarnyi","https://militarnyi.com/en/news/ukraine-drone-avoid-helicopter-hit-tanker/","2026-09-12"),S("Defence Matters","https://defencematters.eu/ukrainian-drone-strikes-armada-leader-off-sochi","2026-09-12")]))
L.append(R("2026-09-16",["unnamed cargo vessel"],[],"cargo","Black Sea (location not reported)","unknown",False,None,None,None,None,"unknown","none","aggregator: Russian forces",False,"not reported",
 [F2T()],note="Low confidence, no detail"))
L.append(R("2026-09-17",["Mariam M"],["Tanzania"],"general cargo (to load wheat at Reni)","Danube Delta near Bystroe Channel, en route to Reni","UA-coast",False,None,None,None,None,"aerial drone","none","Ukraine (Infrastructure Ministry): Russia",False,"captain killed, 3 injured",
 [S("Kyiv Independent","https://kyivindependent.com/russian-drone-attack-on-tanzania-flagged-vessel-kills-captain-injures-3-crew-members-ukraine-says","2026-09-17"),S("ShipFinder","https://www.shipfinder.com/maritime-news/maritime-security/cargo-ship-drone-attack-danube-delta-2026-09-17","2026-09-18")]))
L.append(R("2026-09-23",["unnamed cargo ship (anchored)"],["Antigua and Barbuda"],"cargo","Black Sea, at anchor (Odesa region alert area)","UA-coast",False,None,None,None,None,"aerial drone","none","Ukraine (USPA): Russia",False,"captain (Ukrainian) killed; crew evacuated by Navy",
 [S("Ukrainian News","https://ukranews.com/en/news/1176591-russia-attacks-civilian-vessel-in-black-sea-overnight-captain-killed","2026-09-23"),S("UA.News","https://ua.news/en/war-vs-rf/rf-atakuvala-vantazhne-sudno-v-chornomu-mori-zaginuv-ukrayinskii-kapitan","2026-09-23"),S("ShipFinder","https://www.shipfinder.com/maritime-news/maritime-security/drone-strike-cargo-ship-black-sea","2026-09-23")]))
# ---------------- OCTOBER
L.append(R("2026-10-03",["unnamed general cargo ship"],["Liberia"],"general cargo","port in Odesa region","UA-port",True,None,None,None,None,"unknown","none","Ukraine (USPA): Russia",False,"1 killed (motorman), 3 injured, 13 evacuated",
 [S("Reuters","https://www.reuters.com/world/russia-hits-liberian-flagged-ship-ukraines-odesa-port-kills-one-2026-10-03","2026-10-03"),S("Kyiv Independent","https://kyivindependent.com/russian-strike-on-liberian-flagged-cargo-ship-in-black-sea-kills-1-injures-3/","2026-10-03")]))
L.append(R("2026-10-05",["Royad Mammadov"],["St Kitts and Nevis"],"general cargo (Turkish-owned, corn Izmail->Ravenna)","~20-30 nm off Sfantu Gheorghe, ~9 nm from Pescarus platform, Romanian EEZ","RO-EEZ",False,20,44.45,29.75,"place-approx","aerial drone","none","Zelensky: two Russian drones; Ambrey: highly likely Russian",True,"2 killed, 11 rescued (3 injured), 1 missing (early reports)",
 [S("Euronews","https://www.euronews.com/2026/10/05/drone-reportedly-hits-ship-in-black-sea-killing-two-and-injuring-11","2026-10-05"),S("Metro","https://metro.co.uk/2026/10/05/drone-hits-cargo-ship-black-sea-leaving-a-dozen-missing-29679555/","2026-10-05"),S("Fakti.bg","https://fakti.bg/en/bulgaria/1086903-the-alfa-watan-sunk-by-a-drone-near-byala-came-from-egypt","2026-10-06")],
 note="Distance varies: 20 nm from shore (Euronews), 30 nm south of Sfantu Gheorghe (Fakti); Romanian union says aerial and sea drones"))
L.append(R("2026-10-06",["Alfa Watan","Able"],["Togo","Palau"],"general cargo (Alfa Watan Al Arish->Sulina; Able ex-Galati, wheat)","~70 nm east of Byala, Bulgarian EEZ","BG-EEZ",False,70,42.87,29.5,"place-approx","sea drone","none","Ambrey: highly likely Russian; Zelensky: Russia; Bulgaria: no attribution",True,"Alfa Watan sank, crew missing (search ended); Able: fire, 18 rescued, 2 seriously injured",
 [S("Fakti.bg","https://fakti.bg/en/bulgaria/1086903-the-alfa-watan-sunk-by-a-drone-near-byala-came-from-egypt","2026-10-06"),S("Stars and Stripes","https://www.stripes.com/theaters/europe/2026-10-07/bulgaria-black-sea-drone-attack-23081560.html","2026-10-07"),S("BBC","https://www.bbc.co.uk/news/articles/c8ly0v5r602eo","2026-10-06"),S("Ambrey","https://ambrey.com/operations/event/treat-update-black-sea-merchant-vessel-attacks","2026-10-06")],
 note="Combined aerial + sea drones per Bulgarian military; 'sunk' refers to Alfa Watan only"))
L.append(R("2026-10-06",["unnamed tanker (rapeseed oil)"],["Marshall Islands"],"tanker (vegetable oil)","Black Sea, Odesa region waters","UA-coast",False,None,None,None,None,"aerial drone","none","Ukraine (Kiper): Russia",False,"1 killed (steward), 7 injured",
 [S("Ukrainska Pravda","https://www.pravda.com.ua/eng/news/2026/10/06/8056674/","2026-10-06"),S("Kyiv Independent","https://kyivindependent.com/drones-strike-merchant-vessels-in-black-sea-off-bulgaria-and-ukraine-killing-at-least-one","2026-10-06"),S("BTA","https://www.bta.bg/en/news/1218546-russian-attack-on-ship-flying-marshall-islands-flag-in-black-sea-leaves-one-dead","2026-10-06")]))
L.append(R("2026-10-06",["Aframax Rio"],["Liberia"],"crude oil tanker","~11 km off Sochi","RU-coast",False,6,43.55,39.62,"place-approx","sea drone","none","Russian Transport Ministry: uncrewed boats (Ukrainian)",False,"none; 23 Indian crew rescued; crude burning on water",
 [S("ShipFinder","https://www.shipfinder.com/maritime-news/maritime-security/attack-aframax-rio-sochi","2026-10-08"),S("ET EnergyWorld (citing Reuters)","https://energy.economictimes.indiatimes.com/news/oil-and-gas/ukrainian-drone-attack-sets-fire-to-oil-tanker-carrying-23-indians-off-russias-black-sea-coast-crew-rescued/134762583","2026-10-07"),S("Tech Times","https://www.techtimes.com/articles/328739/20261007/ukrainian-sea-drones-set-sochi-ablaze-hitting-russia-where-sanctions-failed.htm","2026-10-07")],
 note="distance_nm = 11 km converted (~6 nm), from Tech Times citing satellite location"))
L.append(R("2026-10-10",["(Russian MoD claim: bulk carrier delivering military cargo to Odesa)"],[],"bulk carrier","Black Sea, en route to Odesa","UA-coast",False,None,None,None,None,"unknown","Russian Defence Ministry","none",False,"not reported",
 [S("NAMPA / Sputnik (RIA Novosti)","https://www.nampa.org/text/23036521","2026-10-10")],claim_only=True,note="No Ukrainian confirmation found"))
L.append(R("2026-10-13",["Chelsea 3"],["Malta"],"general cargo (Ukrainian-owned, Odesa-registered; Giresun->Giurgiulesti)","15-18 nm east of Byala, Bulgarian EEZ","BG-EEZ",False,18,42.87,28.26,"place-approx","aerial drone","none","none (Bulgaria summoning Russian ambassador per Euronews)",False,"15 crew rescued, 5 light injuries",
 [S("Turkiye Today","https://www.turkiyetoday.com/world/drones-hit-2-ships-off-bulgaria-1-sinks-pm-radev-says-3230199","2026-10-13"),S("The Sofia Globe","https://sofiaglobe.com/2026/10/13/new-drone-attacks-on-ships-in-bulgarias-black-sea-eez-one-sunk/","2026-10-13"),S("Fakti.bg","https://fakti.bg/en/bulgaria/1089511-three-drones-hit-the-ship-chelsea-3-near-byala",None)],
 note="Distance reported as 18 nm (AP/Radev) and 15 nm (Sofia Globe)"))
L.append(R("2026-10-13",["HS Dignity"],["Guinea-Bissau"],"general cargo (IMO 9545912)","17 nm east of Krapets, Bulgarian EEZ","BG-EEZ",False,17,43.63,28.96,"place-approx","aerial drone","none","none",True,"16 crew: 5-6 rescued, 10-11 missing (13.10 evening)",
 [S("The Sofia Globe","https://sofiaglobe.com/2026/10/13/new-drone-attacks-on-ships-in-bulgarias-black-sea-eez-one-sunk/","2026-10-13"),S("Reuters","https://www.reuters.com/world/europe/drone-sinks-ship-off-bulgaria-coast-prime-minister-says-2026-10-13/","2026-10-13"),S("Maritime.bg","https://www.maritime.bg/155789/",None),S("Novinite (HS Dignity identified; Azov Concord was the rescuer, first named in error)","https://www.novinite.com/articles/241028/HS+DIGNITY+Identified+as+Ship+Sunk+Off+Bulgaria%E2%80%99s+Black+Sea+Coast","2026-10-13"),S("BBC","https://www.bbc.com/news/articles/cmn06w5x9g25o","2026-10-13")],
 note="First reports (Sofia Globe, Radev) named the sunk ship Azov Concord(e), St Vincent flag, Turkish owner; corrected 13.10: it was HS Dignity, and Azov Concord picked up 4 survivors"))
L.sort(key=lambda d:(d["date_event"], d.get("aggregate",False)))
with open("ledger.jsonl","w") as f:
    for d in L: f.write(json.dumps(d,ensure_ascii=False)+"\n")
from collections import Counter
c=Counter(); agg=Counter(); single=Counter()
for d in L:
    m=d["date_event"][:7]
    if d.get("aggregate"): agg[m]+=1; continue
    c[(m,d["zone"])]+=1
    if d.get("single_source"): single[m]+=1
for k in sorted(c): print(k,c[k])
print("aggregates",dict(agg)); print("single-source",dict(single)); print("total lines",len(L))
