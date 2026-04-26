# Code Review — Original PoC Script

## What's good

- The overall idea is reasonable, find users who rated the input book, look at what else they read, and rank by Pearson correlation. A standard item based collaborative filtering approach.
- Filtering out `Book-Rating == 0` is correct (those are implicit, not explicit ratings).
- The `min_ratings >= 8` threshold makes sense to drop noisy candidates.

## Main issues

- **Hardcoded paths**: (`'Downloads/BX-Book-Ratings.csv'`) will only work if you run the script from one specific folder.
- **Hardcoded to one book**:  the title `'the fellowship of the ring...'` and author `"tolkien"` appear directly in the code. To recommend something else you have to edit the source.
- **Readability**: everything runs at module scope, no functions
- **No error handling**: missing files, a book that isn't in the dataset, or `NaN` correlations all fail silently or with an unfriendly traceback.
- **Lowercase transformation is broken**: `x.dtype == 'string'` is never true for pandas object columns, so the lambda on line 14 is a no-op. This worked for older Pandas version.
- **Dead code**: `worst_list` is computed but never used.

## What I changed in the refactor

- Wrapped logic into `recommend_books(books, ratings, book_title, author_contains, min_ratings, top_n)` and `load_data()`
- Moved paths and simple runtime settings into `config.ini` and `src/settings.py`.
- Split data loading, cleaning, and recommendation into separate modules.
- Lowercased the relevant columns explicitly so matching is case and whitespace insensitive.
