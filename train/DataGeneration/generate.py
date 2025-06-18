import os
from dotenv import load_dotenv
from SYSTEM_benign import SYSTEM_benign
from SYSTEM_malicious import SYSTEM_malicious
from prompt_utils import *
load_dotenv()

HF_TOKEN=os.environ.get("HF_TOKEN")
os.environ["HF_TOKEN"] =HF_TOKEN
os.environ["HUGGINFACEHUB_API_TOKEN"]=HF_TOKEN
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "true"


import random
from tqdm import tqdm
from vllm import LLM, SamplingParams
import torch
import json

def create_prompts(categories,SYSTEM,behavior="malign"):
    behavior_types = ["Directive", "Inquiry", "Opinion-seeking", "Manipulative"]
    lengths = ["short", "medium", "long"]
    positions = ["beginning", "middle", "end"]
    messages = []
    for category in categories:

        keywords = categories[behavior][category]
        if behavior=="malign":
            cat_description = categories_descriptions[category]

        for key in tqdm(keywords):
            for tone in MANIPULATIVE_TONES:
                for behavior_type in behavior_types:
                    random_length = random.choice(lengths)
                    random_pos = random.choice(positions)
                    tox_level = random.choice(TOXICITY_LEVELS)
                    if behavior=="malign":
                        user_prompt = f"Now, generate the prompt based on the following inputs:\nCategory: {category} -> {cat_description}\nKeyword: {key}\nTone: {tone}\nToxicity:{tox_level}\nLength: {random_length}\nPosition: {random_pos}\nBehavior type: {behavior_type}"
                    else:
                        user_prompt=f"Now, generate the prompt based on the following inputs:\nCategory: {category}\nKeyword: {key}\nTone: {tone}\nLength: {random_length}\nPosition: {random_pos}\nBehavior type: {behavior_type}"

                    messages.append([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_prompt}])
    return messages


def parse_answers(model_answers,behavior="malign"):
    parsed = []
    for item in model_answers:
        prompt = item["answer"]
        if behavior=="malign":
            category,keyword,tone,toxicity,length,position,behavior_type=[x.split(":")[1].strip() for x in item["prompt"].split("\n")[1:]]
            toxicity=toxicity.split("->")[0].strip()
            category=category.split("->")[0].strip()
        else:
            category, keyword, tone, length, position, behavior_type = [x.split(":")[1].strip() for x in
                                                                        item["prompt"].split("\n")[1:]]
            toxicity=""
        tone = tone.split("->")[0].strip()

        if "[[[" not in prompt or "]]]" not in prompt:
            continue
        start, end = (prompt.index("[[[") + 3, prompt.index("]]]"))
        behavior = prompt[start:end]
        prompt = prompt.replace(f"[[[{behavior}]]]", behavior + ".")
        if prompt.startswith(">"):
            prompt = prompt[1:].strip()

        parsed.append({"prompt": prompt, "ann": behavior, "category": category, "tone": tone, "toxicity": toxicity,
                       "behavior_type": behavior_type, "keyword": keyword})
    with open(f"../synth_dataset/{behavior}_dataset.json","w") as f:
        json.dump(parsed,f,indent=2)

def run_generation(messages,sampling_params,behavior="malign"):
    outputs = llm.chat(messages, sampling_params)
    model_answers = []

    for i, output in enumerate(outputs):
        prompt = messages[i][1]["content"]
        generated_text = output.outputs[0].text

        model_answers.append({"prompt": prompt, "answer": generated_text})

    return parse_answers(model_answers,behavior=behavior)



if __name__=="__main__":
    model_id = "Qwen/Qwen3-14B"
    sampling_params = SamplingParams(temperature=0.70, max_tokens=1000)
    llm = LLM(model=model_id, tokenizer="qwen3_noreasoning", dtype=torch.bfloat16, trust_remote_code=True,
              max_model_len=2048)

    malicious_prompts=create_prompts(categories["malign"],SYSTEM_malicious)
    benign_prompts=create_prompts(categories["benign"],SYSTEM_benign,behavior="benign")

    run_generation(malicious_prompts,sampling_params)
    run_generation(benign_prompts,sampling_params,behavior="benign")

