# %%
import pandas as pd
df = pd.read_csv('spelskaparna.csv')

# %%
instagrams = []
facebooks = []
twitters = []
url = 'http://spelskaparna.com/episode/{}/'

for _, row in df.iloc[:2].iterrows():
    number = row['number']
    hashtags = row['hashtags']
    instagram = row['instagram']
    twitter = row['twitter']
    facebook = row['facebook']
    suffix = row['suffix']
    url = url.format(number)
    suffix = suffix.format(url=url)
    instagram_suffix = row['instagram-suffix']
    text = row['text']
    instagram_text = text.format(namn=instagram)
    instagram_text += '\n' + instagram_suffix
    instagram_text += '\n\n' + hashtags
    instagrams.append(instagram_text)
    twitter_text = text.format(namn=twitter)
    twitter_text += '\n' + suffix
    twitter_text += '\n\n' + hashtags
    twitters.append(twitter_text)
    print(text)
    facebook_text = text.format(namn=facebook)
    facebook_text += '\n'+ suffix
    facebooks.append(facebook_text)

d = {'instagram':instagrams, 'facebook':facebooks,
    'twitter':twitters}

converted_df = pd.DataFrame(d)
converted_df.to_csv('buffer.csv')

# %%
