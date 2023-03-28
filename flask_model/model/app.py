from transformers import pipeline
from flask import Flask, request
import json

scorer = pipeline("text-classification")
app = Flask(__name__)


@app.route('/model', methods=['GET'])
def status():
    return "Running"


@app.route('/model', methods=['POST'])
def create_item():
    return json.dumps(scorer(request.get_json()['review'])[0])
