import requests
import pandas as pd
import random
from datetime import datetime

CLIENT_ID = '91efab88fc7f44aaabbd06b31fefdd60'
CLIENT_SECRET = 'f4f59ea77ddc4ba496098f182bbc3c57'

AUTH_URL = 'https://accounts.spotify.com/api/token'

auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']
headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}
BASE_URL = 'https://api.spotify.com/v1/'

artist_id = input("Enter the URI of your favorite artist: ")
req = requests.get(BASE_URL + 'artists/' + artist_id + '/albums',
                   headers=headers,
                   params={'include_groups': 'album', 'limit': 50})
d = req.json()

data = []  # will hold all track info
albums = []  # to keep track of duplicates

# loop over albums and get all tracks
for album in d['items']:
    album_name = album['name']
    trim_name = album_name.split('(')[0].strip()
    if trim_name.upper() in albums or int(album['release_date'][:4]) < 2012:
        continue
    albums.append(trim_name.upper())  # use upper() to standardize
    
    r = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks', headers=headers)
    tracks = r.json()['items']
    for track in tracks:
        f = requests.get(BASE_URL + 'audio-features/' + track['id'], headers=headers)
        f = f.json()
        f.update({
            'track_name': track['name'],
            'album_name': album_name,
            'short_album_name': trim_name,
            'release_date': album['release_date'],
            'album_id': album['id']
        })
        data.append(f)

df = pd.DataFrame(data)
df['release_date'] = pd.to_datetime(df['release_date'])
df = df.sort_values(by='release_date')
df = df.query('short_album_name != "The Song Remains The Same"')
df = df[~df['track_name'].str.contains('Live|Mix|Track')]
df.head()

random.seed(datetime.now())

filename = str(int(10000000000000000*random.random()))
compression_opts = dict(method='zip', archive_name=filename+'.csv')
df.to_csv(filename+'.zip', index=False, compression=compression_opts)

