from __future__ import annotations
from src.model.book_rec import recommend_books

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Book Recommender", layout="centered")
st.title("Book Recommender")
st.write("Enter a book title and get recommendations.")
book_title = st.text_input("Favorite book", placeholder="The Fellowship of the Ring")
top_n = st.slider("Number of recommendations", min_value=5, max_value=20, value=10)
if st.button("Get recommendations"):
    if not book_title.strip():
        st.warning("Please enter a book title.")
    else:
        try:
            with st.spinner("Generating recommendations..."):
                recommendations = recommend_books(
                    book_title=book_title,
                    top_n=top_n,
                )
            st.subheader(f"Recommendations for: {book_title}")
            st.dataframe(recommendations, use_container_width=True, hide_index=True)
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Recommendation failed: {exc}")