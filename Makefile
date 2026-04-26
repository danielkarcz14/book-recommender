.PHONY: install download clean app all

install:
	python -m pip install -r requirements.txt

download:
	python -m src.data.download

clean:
	python -m src.data.clean

app:
	python -m streamlit run streamlit_app.py

all: install download clean app
