# Statement OCR Service
This is a test project using FastAPI and Tesseract. It currently supports the extraction for Public Bank Statement Page 1 only.


# Project Setup
1. Create virtual environment <br>
`python -m venv env`

2. Install from requirements.txt <br>
`source env/bin/activate && pip install -r requirements.txt`

3. Install [Tesseract]([https://duckduckgo.](https://tesseract-ocr.github.io/tessdoc/Installation.html)com).

4. Install packages as follows: <br>
`sudo apt install uvicorn poppler-utils alembic`

5. Create an **.env** file from **sample.env** file and fill in accordingly.

6. Migrate alembic  <br>
`alembic upgrade head`