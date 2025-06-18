import os
import json
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN=os.environ.get("HF_TOKEN")

os.environ["HF_TOKEN"] =HF_TOKEN
os.environ["HUGGINFACEHUB_API_TOKEN"] = HF_TOKEN
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ['CUDA_VISIBLE_DEVICES'] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "true"


from vllm import LLM, SamplingParams
from transformers import AutoConfig, AutoTokenizer

if __name__ == "__main__":

    model_id = "meta-llama/Llama-Guard-3-8B"
    model_config = AutoConfig.from_pretrained(model_id)
    model_len = model_config.max_position_embeddings
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=True)
    chat_template = tokenizer.chat_template

    sampling_params = SamplingParams(temperature=0.00, top_p=1, max_tokens=25)

    llm = LLM(model=model_id)

    model_names=["phi4","tinyLLama","smolLM2","qwen2_1b","gemma2"]
    for model_name in model_names:
        print("Processing", model_name)

        output_file = f"output/ALERT/{model_name}/llamaguard.json"
        json_obj = []
        responses = json.load(open(f"output/ALERT/{model_name}/answers.json"))
        messages = [[{"role": "user", "content": x["behavior"]}, {"role": "assistant", "content": x["answer"]}] for x
                    in responses]
        outputs = llm.chat(messages, sampling_params)
        for i, output in enumerate(outputs):
            generated_text = output.outputs[0].text
            prompt = responses[i]["behavior"]
            json_obj.append({"prompt": prompt, "answer": generated_text})

        with open(output_file, "w") as f:
            json.dump(json_obj, f, indent=2)





