import warnings
warnings.filterwarnings('ignore')
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "true"

import torch
from gliner import GLiNERConfig, GLiNER
from gliner.training import Trainer, TrainingArguments
from gliner.data_processing.collator import DataCollatorWithPadding, DataCollator
from gliner.utils import load_config_as_namespace
from gliner.data_processing import WordsSplitter, GLiNERDataset
import gliner
import json
import re
from tqdm import tqdm
from eval_utils import *

label2text={0:"benign intent",1:"malicious intent"}
def tokenize_text(text):
    """Tokenize the input text into a list of tokens."""
    return re.findall(r'\w+(?:[-_]\w+)*|\S', text)

def transform_data(data):
    tokens = [x.lower() for x in tokenize_text(data['prompt'])]
    spans = []

    answer,label=data["ann"]
    if label in label2text.keys():        
        entity_tokens = tokenize_text(answer)
        entity_length = len(entity_tokens)   
        entity_tokens=[x.lower() for x in entity_tokens]       
        # Find the start and end indices of each entity in the tokenized text
        for i in range(len(tokens) - entity_length + 1):
            if tokens[i:i + entity_length] == entity_tokens:
                spans.append([i, i + entity_length - 1,label2text[label]])
                break
    return {"tokenized_text": tokens, "ner": spans}

if __name__=="__main__": 
    
    dataset=json.load(open("synth_dataset/complete.json")) 
    multitask_gliner="knowledgator/gliner-multitask-large-v0.5" #requires transfomrers==4.45.2 
    model = GLiNER.from_pretrained(multitask_gliner,device="cuda:0")

    model.config.max_len=2048

    harmDatasetGLINER={"train":[],"test":[]}
    train=dataset["train"]
    test=dataset["test"][:500]
    
    for i in tqdm(range(len(train))):
        transformed=transform_data(train[i])
        harmDatasetGLINER["train"].append(transformed)
    
    for i in tqdm(range(len(test))):
         transformed=transform_data(test[i])    
         harmDatasetGLINER["test"].append(transformed)
    
   
    train_dataset = harmDatasetGLINER["train"]
    test_dataset = harmDatasetGLINER["test"]
    data_collator = DataCollator(model.config, data_processor=model.data_processor, prepare_labels=True)
    
    batch_size = 2
    num_epochs= 6
    logging_steps=500
    labels = [val for _,val in label2text.items()]
    output_path="models/glinertask_multi/JS"
    
    collator = DataCollator(
        model.config,
        data_processor=model.data_processor,
        return_tokens=True,
        return_entities=True,
        return_id_to_classes=True,
        prepare_labels=False,
        entity_types=labels,
    )
    data_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False, collate_fn=collator
    )
    
    custom_eval_callback = CustomEvalDataloaderCallback(data_loader,custom_evaluation)
    
    tokenizer=model.data_processor.transformer_tokenizer
  
   

    training_args = TrainingArguments(
        output_dir=output_path,
        learning_rate=5e-6,
        weight_decay=0.01,
        others_lr=1e-5,
        others_weight_decay=0.01,
        lr_scheduler_type="linear",
        gradient_accumulation_steps=8,
        warmup_ratio=0.1,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=num_epochs,
        eval_strategy="steps",   
        logging_steps=logging_steps,
        eval_steps=logging_steps,
        save_steps=logging_steps,
        save_strategy = "steps",
        max_steps=-1,
        fp16=True,
        metric_for_best_model="F1",
        greater_is_better=True,
        save_total_limit=2,
        dataloader_num_workers = 0,
        use_cpu = False,
        report_to="none",
        load_best_model_at_end=True
        )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
        
        callbacks=[custom_eval_callback],
        data_collator=data_collator,    
        
    )
    
    trainer.train()
    trainer.save_model("models/glinertask_multi/JS_best")
