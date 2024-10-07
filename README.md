# Statement OCR Service
This is a test project using FastAPI and Tesseract. It currently supports the extraction for Public Bank Statement Page 1 only.


# Project Setup
1. Create virtual environment
`python -m venv env`

2. Install from requirements.txt
`source env/bin/activate && pip install -r requirements.txt`

3. Install packages as follows:
`sudo apt install uvicorn`
`sudo apt-get install poppler-utils`
`sudo apt install alembic`

4. Create an **.env** file from **sample.env** file and fill in accordingly.

5. Migrate
`alembic upgrade head`