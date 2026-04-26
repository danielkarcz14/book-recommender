import numpy as np
import pandas as pd

from src.settings import CLEANED_BOOKS_FILE as BOOKS_FILE
from src.settings import CLEANED_RATINGS_FILE as RATINGS_FILE
from src.settings import DEFAULT_TOP_N
from src.settings import MIN_RATINGS


def load_data():
    books = pd.read_csv(BOOKS_FILE)
    ratings = pd.read_csv(RATINGS_FILE)
    return books, ratings


def recommend_books(books, ratings, book_title, min_ratings=MIN_RATINGS, top_n=DEFAULT_TOP_N) -> pd.DataFrame:
    dataset = pd.merge(ratings, books, on="ISBN")

    input_book_title = book_title
    book_title = book_title.lower().strip()

    selected_readers = dataset["User-ID"][dataset["Book-Title-Norm"] == book_title]
    selected_readers = np.unique(selected_readers.tolist())
    
    if len(selected_readers) == 0:
        raise ValueError(f"Book '{input_book_title}' not found or not rated.")

    # final dataset
    books_of_selected_readers = dataset[dataset["User-ID"].isin(selected_readers)]

    # Number of ratings per other books in dataset
    number_of_rating_per_book = books_of_selected_readers.groupby(["Book-Title-Norm"]).agg("count").reset_index()

    # select only books which have actually higher number of ratings than threshold
    books_to_compare = number_of_rating_per_book["Book-Title-Norm"][number_of_rating_per_book["User-ID"] >= min_ratings]
    books_to_compare = books_to_compare.tolist()

    if book_title not in books_to_compare:
        return pd.DataFrame(columns=["book", "corr", "avg_rating"])


    ratings_data_raw = books_of_selected_readers[["User-ID", "Book-Rating", "Book-Title-Norm"]][books_of_selected_readers["Book-Title-Norm"].isin(books_to_compare)]

    # group by User and Book and compute mean
    ratings_data_raw_nodup = ratings_data_raw.groupby(["User-ID", "Book-Title-Norm"])["Book-Rating"].mean()
    
    # reset index to see User-ID in every row
    ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

    dataset_for_corr = ratings_data_raw_nodup.pivot(index="User-ID", columns="Book-Title-Norm", values="Book-Rating")

    query_list = [book_title]
    result_list = []

    for query_title in query_list:
        
        # Take out the selected book from correlation dataframe
        dataset_of_other_books = dataset_for_corr.copy(deep=False)
        dataset_of_other_books.drop([query_title], axis=1, inplace=True)

        # empty lists
        book_titles = []
        correlations = []
        avgrating = []

        # corr computation
        for book_title in list(dataset_of_other_books.columns.values):
            book_titles.append(book_title)
            correlations.append(dataset_for_corr[query_title].corr(dataset_of_other_books[book_title]))
            tab = ratings_data_raw[ratings_data_raw["Book-Title-Norm"] == book_title].groupby("Book-Title-Norm")["Book-Rating"].mean()
            avgrating.append(tab.min())

        # final dataframe of all correlation of each book   
        corr_fellowship = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['book','corr','avg_rating'])
        corr_fellowship.head()

        # top 10 books with highest corr
        result_list.append(corr_fellowship.sort_values('corr', ascending = False).head(top_n))

    return result_list[0]
