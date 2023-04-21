import logging
import os
import re
import json
import gzip
from glob import glob
import csv
from pyochre.utils import Command, meta_open


logger = logging.getLogger(__name__)


comment_fields = ['edited', 'id', 'parent_id', 'distinguished', 'created_utc', 'author_flair_text', 'author_flair_css_class', 'controversiality', 'subreddit_id', 'retrieved_on', 'link_id', 'author', 'score', 'gilded', 'stickied', 'body', 'subreddit', 'author_cakeday']

submission_fields = ['link_flair_css_class', 'thumbnail', 'created_utc', 'spoiler', 'locked', 'distinguished', 'hidden', 'stickied', 'quarantine', 'retrieved_on', 'domain', 'title', 'author', 'id', 'num_comments', 'permalink', 'selftext', 'archived', 'url', 'subreddit', 'contest_mode', 'subreddit_id', 'score', 'suggested_sort', 'author_flair_css_class', 'hide_score', 'edited', 'author_flair_text', 'link_flair_text', 'over_18', 'gilded']

combined_fields = list(set(comment_fields + submission_fields)) + ["type", "full_content"]


def expand_range(start, end):
    retval = []
    for month in range(start["month"], 13):
        retval.append((start["year"], month))
    for year in range(start["year"] + 1, end["year"]):
        for month in range(1, 13):
            retval.append((year, month))
    for month in range(1, end["month"] + 1):
        retval.append((end["year"], month))        
    return retval[0:5]


def create_csv_corpus(args, connection):
    with meta_open(args.spec_file, "rt") as ifd, meta_open(args.output, "wt") as ofd:
        otsv = csv.DictWriter(ofd, combined_fields, delimiter="\t")
        otsv.writeheader()
        specs = json.loads(ifd.read())
        for spec in specs:
            subreddits = set([s.lower() for s in spec["subreddits"]])
            subreddit_rx = re.compile(r".*({}).*".format("|".join(subreddits)), re.I)
            for year, month in expand_range(spec["start"], spec["end"]):
                print(year, month)
                fnames = glob(os.path.join(args.reddit_path, "comments", "RC_{}-{:02}.*".format(year, month)))
                assert len(fnames) == 1
                with meta_open(fnames[0], "rt") as ifd:
                    for line in ifd:
                        j = json.loads(line)
                        if j.get("subreddit", "").lower() in subreddits:
                            j["full_content"] = j["body"].replace("\n", " ")
                            j["type"] = "comment"
                            otsv.writerow({k : v for k, v in j.items() if k in combined_fields})
                # body

                fnames = glob(os.path.join(args.reddit_path, "submissions", "RS_{}-{:02}.*".format(year, month)))
                assert len(fnames) == 1
                with meta_open(fnames[0], "rt") as ifd:
                    for line in ifd:
                        #if subreddit_rx.match(line):
                            
                        #    pass
                        j = json.loads(line)
                        if j.get("subreddit", "").lower() in subreddits:
                            j["full_content"] = j["selftext"].replace("\n", " ")
                            j["type"] = "submission"
                            otsv.writerow({k : v for k, v in j.items() if k in combined_fields})
                        #print(list(j.keys()))
                        #sys.exit()

class RedditCommand(Command):
    
    def __init__(self):
        super(RedditCommand, self).__init__(
            prog="python -m pyochre.extensions.reddit"
        )
        create_csv_corpus_parser = self.subparsers.add_parser(
            "create_csv_corpus",
            help="This command depends on a local mirror of Reddit"
        )
        create_csv_corpus_parser.set_defaults(func=create_csv_corpus)
        create_csv_corpus_parser.add_argument(
            "--reddit_path",
            dest="reddit_path",
            required=True,
            help="Path to Reddit mirror"
        )
        create_csv_corpus_parser.add_argument(
            "--spec_file",
            dest="spec_file",
            required=True,
            help="JSON spec of the materials to extract"
        )
        create_csv_corpus_parser.add_argument(
            "--output",
            dest="output",
            required=True,
            help="CSV file to save corpus as"
        )


if __name__ == "__main__":
    RedditCommand().run()
