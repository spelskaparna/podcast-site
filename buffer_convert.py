# %%
import numpy as np
import pandas as pd

df = pd.read_csv("social.csv")

default_insta_suffix = "Länk finns i bio."
default_suffix = "Hela avsnittet: {url}"

df["instagram_suffix"] = df["instagram_suffix"].fillna(default_insta_suffix)
df["suffix"] = df["suffix"].fillna(default_suffix)

# %%
instagrams = []
facebooks = []
twitters = []
url_template = "http://spelskaparna.com/episode/{}/"

for _, row in df.iterrows():
    number = row["number"]
    hashtags = row["hashtags"]
    instagram = row["instagram"]
    twitter = row["twitter"]
    facebook = row["facebook"]
    if type(twitter) != str and np.isnan(twitter):
        twitter = instagram
    if type(facebook) != str and np.isnan(facebook):
        facebook = instagram
    suffix = row["suffix"]
    url = url_template.format(int(number))
    suffix = suffix.format(url=url)
    instagram_suffix = row["instagram_suffix"]
    text = row["text"]
    instagram_text = text.format(namn=instagram)
    instagram_text += "\n" + instagram_suffix
    instagram_text += "\n\n" + hashtags
    instagrams.append(instagram_text)
    twitter_text = text.format(namn=twitter)
    twitter_text += "\n" + suffix
    twitter_text += "\n\n" + hashtags
    twitters.append(twitter_text)
    print(text)
    facebook_text = text.format(namn=facebook)
    facebook_text += "\n" + suffix
    facebooks.append(facebook_text)

d = {"instagram": instagrams, "facebook": facebooks, "twitter": twitters}

converted_df = pd.DataFrame(d)
converted_df.to_csv("buffer.csv")

# %%
