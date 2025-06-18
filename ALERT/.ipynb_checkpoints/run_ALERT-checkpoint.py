import os
from dotenv import load_dotenv
from model_config import model_ids
from vllm import  LLM, SamplingParams
import json
from tqdm import tqdm

load_dotenv()

HF_TOKEN=os.environ.get("HF_TOKEN")
os.environ["HF_TOKEN"] =HF_TOKEN

os.environ["HUGGINFACEHUB_API_TOKEN"]=HF_TOKEN
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "true"
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="tinyLLama")


import pandas as pd
if __name__=="__main__":
    alert_df = pd.read_json("behaviors/ALERT/alert.jsonl", lines=True)
    alert_df["text"] = alert_df["prompt"].apply(lambda x: x.split("\n")[1].lower())
    alert_behaviors = alert_df["text"].values.tolist()
    sampling_params = SamplingParams(temperature=0.00, top_p=1,max_tokens=1000)
    behaviors_as_messages = [[{"role": "user", "content": b}] for b in alert_behaviors]
    args = parser.parse_args()
    model_name = args.model

    model_id=model_ids[model_name]
    print("Processing",model_name)
    if not os.path.exists(f"output/ALERT/{model_name}"):
        os.mkdir(f"output/ALERT/{model_name}")

    llm = LLM(model=model_id,max_model_len=4096)

    outputs = llm.chat(behaviors_as_messages, sampling_params)
    model_answers = []

    for i, output in enumerate(tqdm(outputs)):
        behavior = alert_behaviors[i]
        generated_text = output.outputs[0].text

        model_answers.append({"behavior": behavior, "answer": generated_text})
    with open(f"output/ALERT/{model_name}/answers.json", "w") as f:
        json.dump(model_answers, f, indent=2)
