from twitter.search import Search
from twitter.scraper import Scraper
import pandas as pd

email, username, password = "b10705052@ntu.edu.tw", "yehyouming", "Ym911216"

search = Search(email, username, password, save=False, debug=1)
scraper = Scraper(email, username, password, debug=1, save=False)

res = search.run(
    limit=1,
    retries=1,
    queries=[{"category": "Top", "query": "ai"}],
)

# get the first tweet
r = res[0][0]

if r["content"]["itemContent"]["tweet_results"]["result"]["__typename"] == "Tweet":
    full_text = r["content"]["itemContent"]["tweet_results"]["result"]["legacy"][
        "full_text"
    ]
    rest_id = r["content"]["itemContent"]["tweet_results"]["result"]["rest_id"]
    print("tweet id:", rest_id)

    tweets_details = scraper.tweets_details([rest_id], count=100, limit=100)

    df_tweets_details = (
        pd.json_normalize(
            tweets_details,
            record_path=[
                "data",
                "threaded_conversation_with_injections_v2",
                "instructions",
            ],
        )["entries"]
        .dropna()
        .explode()
        .apply(pd.Series)["content"]
        .apply(pd.Series)["items"]
        .dropna()
        .explode()
        .apply(pd.Series)["item"]
        .apply(pd.Series)["itemContent"]
        .apply(pd.Series)
        .pipe(lambda df: df[df["__typename"] != "TimelineTimelineCursor"])[
            "tweet_results"
        ]
        .apply(pd.Series)["result"]
        .apply(pd.Series)
        .pipe(lambda df: df[df["__typename"] != "TweetWithVisibilityResults"])["legacy"]
        .apply(pd.Series)
        .pipe(lambda x: pd.concat([x, x["entities"].apply(pd.Series)], axis=1))
        .assign(created_at=lambda x: pd.to_datetime(x["created_at"]))
        .sort_values("created_at", ascending=False)
        .reset_index(drop=True)
        .drop("entities", axis=1)[
            [
                "created_at",
                "id_str",
                "user_id_str",
                "full_text",
                "favorite_count",
                "urls",
                "hashtags",
                "user_mentions",
            ]
        ]
    )
   
# store the tweets details in a csv file
df_tweets_details.to_csv("tweets_details.csv", index=False)
