import json
import os
from transformers import AutoTokenizer
from vllm import SamplingParams
import argparse
from model_config import model_ids
import ray
from transformers import AutoConfig


from ray.data.llm import build_llm_processor, vLLMEngineProcessorConfig

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="tinyLLama")
parser.add_argument("--attack", type=str, default="SAP200")
sampling_params = SamplingParams(temperature=0.00, top_p=1, max_tokens=500)


def run_attack_ray(jailbreak_method="SAP200",model_name="smolLM2"):
    model_id = model_ids[model_name]
    jailbreaked_prompts = []

    try:
      model_config = AutoConfig.from_pretrained(model_id)
      model_len= model_config.max_position_embeddings
    except:
      tokenizer=AutoTokenizer.from_pretrained(model_id)
      model_len=tokenizer.model_max_length
    
    if not os.path.exists(f"output/{model_name}"):
        os.mkdir(f"output/{model_name}")
    
    if jailbreak_method == "SAP200":
        categories = os.listdir("attacks2test/SAP200/")
        for category in categories:
            attack = json.load(open(f"attacks2test/SAP200/{category}/generated_cases.json"))
            for item in attack:
                jailbreaked_prompts.append({"category": category, "prompt": item["Attack Prompt"]})

    if jailbreak_method=="DAN":
        dan=json.load(open("attacks2test/DAN/Dan_samples.json", "r"))
        jailbreaked_prompts=[{"prompt":item["full_prompt"]} for item in dan]
    if jailbreak_method=="DeepInception":
        deep_inception=json.load(open("attacks2test/DeepInception/data.json", "r"))
        jailbreaked_prompts=[{"prompt":item["inception_attack"]} for item in deep_inception]
    print("Loading model ", model_id)
    config = vLLMEngineProcessorConfig(
        model_source=model_id,
        engine_kwargs={
            "enable_chunked_prefill": True,
            "max_num_batched_tokens": 4096,
            "max_model_len": model_len,
        },
        concurrency=1,
        batch_size=64,
    )
    ds = ray.data.from_items([{"text": item["prompt"]} for item in jailbreaked_prompts])
    # Create a Processor object, which will be used to
    # do batch inference on the dataset
    vllm_processor = build_llm_processor(
        config,
        preprocess=lambda row: dict(
            messages=[ {
                "role": "user",
                "content": row["text"]
            }],
            sampling_params=dict(
                temperature=0.0,
                max_tokens=1000,
            )),
        postprocess=lambda row: dict(
            answer=row["generated_text"],
            **row
        ),
    )

    ds = vllm_processor(ds)

    results = ds.take_all()
    output_file = f"output/{model_name}/{jailbreak_method}.json"
    json_obj=[]
    for r in results:
        json_obj.append({"prompt":r["text"],"answer":r["answer"]})
    with open(output_file,"w") as f:
        json.dump(json_obj,f,indent=2)



if __name__ == "__main__":

    args = parser.parse_args()
    model_name = args.model
    attack_method=args.attack
    

    run_attack_ray(jailbreak_method=attack_method,model_name=model_name)

