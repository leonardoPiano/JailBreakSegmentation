# Small but Dangerous: Evaluating and Mitigating Jailbreak Vulnerabilities in Small Language Models
This repository host the dataset and experimental data presented in the paper.

# 📖 Abstract

Small language models (SLMs) are gaining traction as attractive alternatives to large-scale LLMs due to their low computational
cost, suitability for on-device inference, and reduced environmental footprint. As efforts intensify to compress and distill powerful language capabilities into smaller architectures, SLMs are increasingly deployed in
edge devices, embedded systems, and offline applications. However, the safety and alignment properties of these models remain underexplored.
In this work, we identify and characterise a critical blind spot: the misalignment of SLMs and their vulnerability to unsafe behaviour and jailbreak attacks. We introduce a two-phase evaluation pipeline: first, we
test a suite of direct malicious prompts against a range of SLMs; secondly, we apply more sophisticated, tailored jailbreak attacks typically used to circumvent the safety filters of larger, more aligned models. 
Notably, some SLMs that initially appear safe under naive testing, turn out to be highly susceptible to jailbreak prompts—revealing a discrepancy between perceived and actual safety. To address this, we propose
a lightweight mitigation strategy tailored for resource-constrained models, capable of intercepting jailbreak attempts at inference time without requiring retraining. Our findings underscore the urgent need to extend
safety auditing, evaluation benchmarks, and mitigation strategies to the rapidly growing class of small-scale language models.

# Quick-start
TODO
# acknowledgements
This project is supported by the European Union’s HORIZON Research and Innovation Programme under grant agreement No. 101120657, project ENFIELD (European Lighthouse to Manifest Trustworthy and Green AI) <br>
<img src="https://www.enfield-project.eu/sites/default/files/Enfield_logo.png" alt="Logo" width="200">
