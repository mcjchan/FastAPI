import os
from enum import Enum
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from ibm_watson_machine_learning.foundation_models import Model
from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import time

# uvicorn main:app --reload

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


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Deploy Python FastAPI on AWS EC2!"}


@app.post("/generate/")
async def llama_model(model_parameter: ModelParameters):
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

    job_id = uuid.uuid4()
    result = model.generate_text(prompt=model_parameter.input)

    with open(str(job_id)+'.txt', 'w') as f:
        f.write(result)

    response = {"job_id": job_id, "model_response": result}

    return response

@app.post("/check/")
async def check_output(job_parameter: JobParameter):
    filename = job_parameter.job_id+'.txt'

    while True:
        if os.path.isfile(filename):
            with open(filename, encoding="utf8") as f:
                generated_text = f.readlines()
            break
        else:
            time.sleep(5)

    # os.remove(filename)
    result = {"model_response": generated_text}
    return result