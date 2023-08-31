from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class Nsql:
    tokenizer = None
    model = None

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("NumbersStation/nsql-2B")
        self.model = AutoModelForCausalLM.from_pretrained("NumbersStation/nsql-2B", torch_dtype=torch.float16).to(0)


nsql = Nsql()


def generateQuery(text, max_tokens):
    input_ids = nsql.tokenizer(text, return_tensors="pt").input_ids.to(0)
    generated_ids = nsql.model.generate(input_ids, max_length=max_tokens)
    query = nsql.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return query
