#!/bin/bash
# model to test
models=("phi4" "tinyLLama" "smolLM2" "qwen2_1b" "gemma2") 

attacks=("DAN" "DeepInception" "SAP200")
for model in "${models[@]}"; do
    
    for attack in "${attacks[@]}"; do
      echo " Starting : $model with $attack attack method"
      #lunch script
      python3 run_attack.py --model "$model" --attack "$attack" 

      
      echo "Completed: $model"
    
    done

done
