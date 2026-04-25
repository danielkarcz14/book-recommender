from __future__ import annotations
import streamlit as st
from src.model.book_rec import load_data, recommend_books


@st.cache_data
def get_data():
    return load_data()


st.set_page_config(page_title="Book Recommender", layout="centered")
st.title("Book Recommender")
st.write("Enter a book title and get recommendations.")

books, ratings = get_data()

book_title = st.text_input("Favorite book", placeholder="The Fellowship of the Ring")
top_n = st.slider("Number of recommendations", min_value=5, max_value=20, value=10)
if st.button("Get recommendations"):
    if not book_title.strip():
        st.warning("Please enter a book title.")
    else:
        try:
            with st.spinner("Generating recommendations..."):
                recommendations = recommend_books(
                    books=books,
                    ratings=ratings,
                    book_title=book_title,
                    top_n=top_n,
                )
            st.subheader(f"Recommendations for: {book_title}")
            st.dataframe(recommendations, use_container_width=True, hide_index=True)
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Recommendation failed: {exc}")