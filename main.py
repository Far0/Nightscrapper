import requests
import sys
from bs4 import BeautifulSoup
import json
from os.path import exists
import os
broadcaster_bid = []
broadcaster_id = []
session = requests.Session()
data ={}
data['streamers'] = []
header = {"Authorization":"Bearer -", 
          "Client-Id":"-"}

def main():
    v = updater()
    FetchBID(0)
    createBroadcasterArrays(4)
    nrClipuri = 2
    for i in broadcaster_bid:
        getTopClips(nrClipuri,i)
    for i in broadcaster_id:
        checkProfilePicture(i)
    downloadClips()

def updater():
    ## u can delete the updater function or manually update variable v to 999
    v = 1
    try:
        v_github = int(requests.get('https://raw.githubusercontent.com/Far0/Nightscrapper/main/vers.ini', stream=True).text)
        if v > v_github:
            beta = 1 # activates experimental features
            print('Nightscrapper V', v , "BETA")
            return 1
        elif v < v_github:
            print('Folosești o versiune veche de Nightscrapper , V' , v , ' ultima versiune este V ' , v_github)
            return 2
        print('Nightscrapper V' , v)
        return 0
    except:
        print('A apărut o eroare la nivelul updater-ului, dezactivez funcția de auto-update') 
        beta = 0
        print('Nightscrapper V' , v)
        return 2

def FetchBID(j):
    f = open('Streamers.json')
    data = json.load(f)
    for i in range(nrStreameri(j)):
        if data['streamers'][str(j)][i]['bid'] == "":
            twitch_api = get_userinfo(data['streamers'][str(j)][i]['name']) # Iau userinfo  cu nume din ()
            data['streamers'][str(j)][i]['bid'] = twitch_api['data'][0]["id"]
    with open('Streamers.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
    f.close()
    outfile.close()
    if not(j == 3):
        return FetchBID(j+1)


def getTopClips(nr, streamer):

    response = session.get('https://api.twitch.tv/helix/clips?broadcaster_id=' + streamer +'&first=' + str(nr+1) +"&started_at=" + "2021-12-20T15:04:05Z", headers=header)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    twitch_api = json.loads(html_soup.text)
    i = 0
    print (twitch_api)
    for i in range(nr):
        url = twitch_api['data'][i]['thumbnail_url']
        mp4_url = url[:url.index("-preview")] + '.mp4'
        data['streamers'].append({
        'streamer': twitch_api['data'][i]['broadcaster_name'],
        'url': twitch_api['data'][i]['url'],
        'downloadurl': mp4_url,
        'views': twitch_api['data'][i]['view_count'],
        'title': twitch_api['data'][i]['title'],
        'gameid': twitch_api['data'][i]['game_id']
})
        with open('Clips.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)

def createBroadcasterArrays(nr):
    f = open('Streamers.json')
    data = json.load(f)
    if nr == 4:
        for j in range(4):
            for i in range(nrStreameri(str(j))):
                broadcaster_bid.append(data['streamers'][str(j)][i]["bid"])
                broadcaster_id.append(data['streamers'][str(j)][i]["name"])
    else:
        for i in range(nrStreameri(str(nr))):
            broadcaster_bid.append(data['streamers'][nr][i]["bid"])
            broadcaster_id.append(data['streamers'][nr][i]["name"])
    f.close()

def downloadClips(): #SAFE
    f = open('Clips.json')
    data = json.load(f)
    for i in data['streamers']:
        print (i)
        download = requests.get(i['downloadurl'])
        nume = i['downloadurl']
        nume = nume.split("/")[-1:]
        nume = nume[0]
        mp4download = open('./Clips/' + nume , "wb")
        for chunk in download.iter_content(chunk_size=255): 
            if chunk: 
                mp4download.write(chunk)
        f.close()
        mp4download.close()


def checkProfilePicture(streamer):
    path = "pp/" + streamer + ".png"
    url = get_userinfo(streamer)['data'][0]['profile_image_url']
    try:
        os.remove(path) 
    except:
        print ("I didn't find the profile picture for " + streamer)
    r = requests.get(url, stream = True)
    f = open( path, "wb")
    f.write(r.content)
    f.close()
    print ('Downloaded ' + streamer + '.png')


    
def get_userinfo(streamer):
    response = session.get('https://api.twitch.tv/helix/users?login=' + streamer , headers=header)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    twitch_api = json.loads(html_soup.text)
    return twitch_api

def nrStreameri(tip):
    f = open('Streamers.json')
    data = json.load(f)
    f.close()
    if tip == 4:
        return len(data['streamers']['0'])+len(data['streamers']['1'])+len(data['streamers']['2'])+len(data['streamers']['3'])
    return len(data['streamers'][str(tip)])

main()