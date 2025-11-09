#!/bin/bash
# model to test
models=("phi4" "tinyLLama" "smolLM2" "qwen2_1b" "gemma2") 

for model in "${models[@]}"; do    
   
    echo " Starting : $model "
    #lunch script
    python3 run_attack.py --model "$model"

      
    echo "Completed: $model"
    
 

done
