import json
import pandas as pd
import requests
import numpy as np

print("##### Youtube RTHK Backup - Contributor120 #####")

youtube_json = "rthk.json"
sheet_id = "1JPyevWnxvoq_xzY4ptOgaTaTYSLE9oMva66kxm66K0k"
gid = "1552175605"
google_csv_url = "https://docs.google.com/spreadsheets/d/<sheetid>/export?format=csv&id=<sheetid>&gid=<gid>"

# optional (makes it a bit less sad)
youtube_dl_log = "archive.log"

### Download the dumps from this kind person:
# https://www.reddit.com/r/DataHoarder/comments/n3pvnm/hong_kong_broadcaster_rthk_to_delete_shows_over_a/gwtqsv2/
with open(youtube_json, 'r') as file:
    data = json.loads(file.read())

# Change the data around a bit (ok if still messy)
df = pd.DataFrame(data)
del data

print("Number of entires in metadata archive: ", len(df))

# hardcoded, whatever
keys = ['id', 'title', 'unpublished']
for key in keys:
    df[key] = df.videos.apply(lambda x: x[key])
    
del key, keys

### Now crosscheck with the google sheet:
res= requests.get(url=google_csv_url.replace('<sheetid>', sheet_id).replace('<gid>', gid))
open('google.csv', 'wb').write(res.content)

df_goog = pd.read_csv('google.csv', skiprows=[0])

def f(string):
    try: 
        assert "youtu.be" in string or "youtube.com" in string
        res = string.split('/')[-1]
        if 'watch' in res:
            res = res.split('=')[1]
        res = res.split('&')[0]
    except:
        # youtube IDs are 11 in length
        try:
            if len(string) == 11:
                res = string
            else:
                res = np.nan
        except:
            res = np.nan
    return res
    

df_goog['id'] = df_goog['Youtube Link'].apply(f)
df_goog['sheet_entry'] = True
df_goog['sheet_line'] = df_goog.index + 2

# Now merge to see what is still needed
df_full = df[['id', 'title', 'unpublished']].merge(
            df_goog[['id', 'Backup Link', 'sheet_entry', 'sheet_line']],
            on='id', how='left')

# If there's a youtube_dl log

if youtube_dl_log != None and youtube_dl_log != '':
    df_ydl = pd.read_csv('archive.log', delimiter=' ', header=None, names=['source', 'id'])
    df_ydl['youtube_dl_entry_contributor120'] = True
    
    df_full = df_full.merge(
            df_ydl[['id', 'youtube_dl_entry_contributor120']],
            on='id', how='left')
    
# add a column saying if it's found
def checker(row):
    if 'youtube_dl_entry_contributor120' in row.keys():
        return row['youtube_dl_entry_contributor120'] == True or row['sheet_entry'] == True
    else:
        return row['sheet_entry']
df_full['Backup_found'] = df_full.apply(checker, axis=1)

print("Number of files confirmed backed up: ", len(df_full[df_full['Backup_found']==True]))

df_full.to_csv('status.csv')

df_goog.to_csv('google.csv')
df_ydl.to_csv('youtubedl.csv')
