import os
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models import Model
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uuid
import time
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from googlesearch import search
import re

# uvicorn main:app --reload
app = FastAPI()


class ModelParameters(BaseModel):
    decoding_method: str
    temperature: float
    max_new_tokens: int
    min_new_tokens: int
    repetition_penalty: float
    stop_sequences: list = []
    model_id: str
    input: str
    project_id: str
    api_key: str


class JobParameter(BaseModel):
    job_id: str


class StockParameter(BaseModel):
    stock: str


class NewsParameter(BaseModel):
    stock_symbol: str


def aastock_news(stock_symbol):

    if re.search(r"\.HK$", stock_symbol):
        url = "https://www.aastocks.com/tc/stocks/analysis/stock-aafn/0" + stock_symbol.split(".HK")[0]
    else:
        url = "http://www.aastocks.com/tc/usq/quote/stock-news.aspx?symbol=" + stock_symbol

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    headers = soup.find_all("div", {"class": lambda x: x and x.startswith("newshead") and x.endswith("lettersp2")})
    headers = [title.text.strip() for title in headers]

    contents = soup.find_all("div", {"class": lambda x: x and x.startswith("newscontent") and x.endswith("lettersp2")})
    contents = [description.text.strip().replace('\n', '').replace('"', '') for description in contents]

    zipped_lists = zip(headers, contents)

    latest_news = ""
    for header, content in zipped_lists:
        latest_news += f"NewsTitle: {header}\nNewsContent: {content}\n"

    return latest_news


def historical_stock_data(stock_symbol):
    stock = yf.Ticker(stock_symbol)

    # get historical market data
    hist = stock.history(period="1mo")
    hist_str = hist.to_string()

    return hist_str

def write_generated_text(model_parameter: ModelParameters, job_id):
    credentials = {
        "url": "https://us-south.ml.cloud.ibm.com",
        "apikey": model_parameter.api_key
    }

    project_id = model_parameter.project_id

    model_id = model_parameter.model_id

    parameters = {
        GenParams.MAX_NEW_TOKENS: model_parameter.max_new_tokens,
        GenParams.MIN_NEW_TOKENS: model_parameter.min_new_tokens,
        GenParams.DECODING_METHOD: model_parameter.decoding_method,
        GenParams.REPETITION_PENALTY: model_parameter.repetition_penalty
    }

    model = Model(
        model_id=model_id,
        params=parameters,
        credentials=credentials,
        project_id=project_id)

    result = model.generate_text(prompt=model_parameter.input)

    with open(str(job_id)+'.txt', 'w', encoding='utf-8') as f:
        f.write(result)

@app.get("/")
async def root():
    return {"message": "Deploy Python FastAPI on AWS EC2!"}


@app.post("/generate/")
async def llama_model(model_parameter: ModelParameters, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4()

    background_tasks.add_task(write_generated_text, model_parameter, job_id)

    return {"job_id": job_id}


@app.post("/check/")
async def check_output(job_parameter: JobParameter):
    filename = job_parameter.job_id+'.txt'

    while True:
        if os.path.isfile(filename):
            with open(filename, encoding="utf8") as txtfile:
                generated_text = txtfile.read()
            result = {"model_response": generated_text}
            os.remove(filename)
            return result
        else:
            time.sleep(5)

    # os.remove(filename)

@app.post("/stock/")
async def check_symbol(stock_parameter: StockParameter):
    query = stock_parameter.stock + " stock symbol"
    results = search(query, advanced=True, num_results=1)
    title = next(results).title

    pattern = r"(.+)\((.+)\)"
    match = re.search(pattern, title)
    stock, symbol = match.groups()
    # print(f"Stock: {stock.strip()}")
    # print(f"Symbol: {symbol}")

    symbol_response = {
        "stock": stock,
        "symbol": symbol
    }

    # Return the JSON response
    return symbol_response


@app.post("/news/")
async def related_news(news_parameter: NewsParameter, background_tasks: BackgroundTasks):
    stock_symbol = news_parameter.stock_symbol

    latest_news = aastock_news(stock_symbol)

    news = "股票最近一個月的股價變動\n" + historical_stock_data(stock_symbol) + "\n"
    news += latest_news

    return {"related_news": news}

@app.post("/comparison/")
async def compare_stocks(news_parameter: NewsParameter):
    stock_symbol = news_parameter.stock_symbol

    latest_news = aastock_news(stock_symbol)

    return {"stocks_news": latest_news}

