from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class Nsql:
    tokenizer = None
    model = None

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("NumbersStation/nsql-2B")
        self.model = AutoModelForCausalLM.from_pretrained("NumbersStation/nsql-2B", torch_dtype=torch.float16).to(0)


class SqlCoder:
    tokenizer = None
    model = None

    def __init__(self):
        model_name = "defog/sqlcoder"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            load_in_8bit=True,
            #     load_in_4bit=True,
            device_map="auto",
            use_cache=True,
        )


# nsql = Nsql()
sqlCoder = SqlCoder()


# def generateQueryUsingNsql(text, max_tokens):
#     input_ids = nsql.tokenizer(text, return_tensors="pt").input_ids.to(0)
#     generated_ids = nsql.model.generate(input_ids, max_length=max_tokens)
#     query = nsql.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
#     return query


def generateQueryUsingSqlCoder(prompt, tokens):
    eos_token_id = sqlCoder.tokenizer.convert_tokens_to_ids(["```"])[0]
    inputs = sqlCoder.tokenizer(prompt, return_tensors="pt").to("cuda")
    generated_ids = sqlCoder.model.generate(
        **inputs,
        num_return_sequences=1,
        eos_token_id=eos_token_id,
        pad_token_id=eos_token_id,
        max_new_tokens=tokens,
        do_sample=False,
        num_beams=5
    )
    outputs = sqlCoder.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    torch.cuda.empty_cache()
    query = outputs[0].split("```sql")[-1].split("```")[0].split(";")[0].strip() + ";"
    return query
