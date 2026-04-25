from pathlib import Path
import sys

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.paths import CLEANED_BOOKS_FILE as BOOKS_FILE
from src.paths import CLEANED_RATINGS_FILE as RATINGS_FILE


def load_data():
    books = pd.read_csv(BOOKS_FILE)
    ratings = pd.read_csv(RATINGS_FILE)
    return books, ratings


def recommend_books(books, ratings, book_title, author_contains=None, min_ratings=8, top_n=10):
    dataset = pd.merge(ratings, books, on="ISBN")

    dataset["Book-Title"] = dataset["Book-Title"].astype(str).str.lower().str.strip()
    dataset["Book-Author"] = dataset["Book-Author"].astype(str).str.lower().str.strip()

    book_title = book_title.lower().strip()

    selected_readers = dataset["User-ID"][dataset["Book-Title"] == book_title]

    if author_contains:
        author_contains = author_contains.lower().strip()
        selected_readers = dataset["User-ID"][
            (dataset["Book-Title"] == book_title)
            & (dataset["Book-Author"].str.contains(author_contains, na=False))
        ]

    selected_readers = np.unique(selected_readers.tolist())
    books_of_selected_readers = dataset[dataset["User-ID"].isin(selected_readers)]
    number_of_rating_per_book = books_of_selected_readers.groupby(["Book-Title"]).agg("count").reset_index()

    books_to_compare = number_of_rating_per_book["Book-Title"][
        number_of_rating_per_book["User-ID"] >= min_ratings
    ].tolist()

    ratings_data_raw = books_of_selected_readers[["User-ID", "Book-Rating", "Book-Title"]][
        books_of_selected_readers["Book-Title"].isin(books_to_compare)
    ]

    ratings_data_raw_nodup = ratings_data_raw.groupby(["User-ID", "Book-Title"])["Book-Rating"].mean()
    ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

    dataset_for_corr = ratings_data_raw_nodup.pivot(index="User-ID", columns="Book-Title", values="Book-Rating")

    LoR_list = [book_title]
    result_list = []
    worst_list = []

    for LoR_book in LoR_list:
        
        #Take out the Lord of the Rings selected book from correlation dataframe
        dataset_of_other_books = dataset_for_corr.copy(deep=False)
        dataset_of_other_books.drop([LoR_book], axis=1, inplace=True)
        
        # empty lists
        book_titles = []
        correlations = []
        avgrating = []

        # corr computation
        for book_title in list(dataset_of_other_books.columns.values):
            book_titles.append(book_title)
            correlations.append(dataset_for_corr[LoR_book].corr(dataset_of_other_books[book_title]))
            tab=ratings_data_raw[ratings_data_raw['Book-Title']==book_title].groupby(ratings_data_raw['Book-Title'])['Book-Rating'].mean()
            avgrating.append(tab.min())

        # final dataframe of all correlation of each book   
        corr_fellowship = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['book','corr','avg_rating'])
        corr_fellowship.head()

        # top 10 books with highest corr
        result_list.append(corr_fellowship.sort_values('corr', ascending = False).head(top_n))
        
        #worst 10 books
        worst_list.append(corr_fellowship.sort_values('corr', ascending = False).tail(10))

    return result_list[0]

