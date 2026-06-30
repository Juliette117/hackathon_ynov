"""
Fine-tuning LoRA (QLoRA) — Modèle Médical Expérimental
À exécuter sur Google Colab Pro (GPU T4 minimum)

Instructions :
1. Ouvrir Google Colab : colab.research.google.com
2. Activer un GPU : Exécution > Modifier le type d'exécution > T4 GPU
3. Copier ce script et exécuter cellule par cellule
"""

# ==============================================================
# CELLULE 1 — Installation
# ==============================================================
# !pip install -q transformers peft datasets accelerate bitsandbytes trl

# ==============================================================
# CELLULE 2 — Imports et vérification GPU
# ==============================================================
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer

print(f"GPU disponible : {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU : {torch.cuda.get_device_name(0)}")
    print(f"VRAM : {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# ==============================================================
# CELLULE 3 — Configuration
# ==============================================================
MODEL_NAME   = "microsoft/phi-2"
DATASET_NAME = "ruslanmv/ai-medical-chatbot"
OUTPUT_DIR   = "./phi2-medical-lora"
MAX_SAMPLES  = 2000
MAX_SEQ_LEN  = 512

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# ==============================================================
# CELLULE 4 — Chargement et préparation du dataset médical
# ==============================================================
print("Chargement du dataset médical (ruslanmv/ai-medical-chatbot)...")
dataset = load_dataset(DATASET_NAME, split="train")
dataset = dataset.select(range(min(MAX_SAMPLES, len(dataset))))
print(f"Exemples chargés : {len(dataset)}")
print("Colonnes disponibles :", dataset.column_names)
print("Exemple :", dataset[0])

def format_conversation(example):
    patient = example.get("Patient", example.get("input", ""))
    doctor  = example.get("Doctor",  example.get("output", ""))
    return {"text": f"<|user|>\n{patient}<|end|>\n<|assistant|>\n{doctor}<|end|>"}

dataset = dataset.map(format_conversation, remove_columns=dataset.column_names)
print("\nDataset formaté. Exemple :")
print(dataset[0]["text"][:400])

# ==============================================================
# CELLULE 5 — Chargement modèle + tokenizer
# ==============================================================
print(f"\nChargement de {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
model.config.use_cache = False
print("Modèle chargé avec quantization 4-bit.")

# ==============================================================
# CELLULE 6 — Configuration LoRA
# ==============================================================
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "dense"],
    bias="none",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ==============================================================
# CELLULE 7 — Entraînement
# ==============================================================
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=2,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.05,
    logging_steps=25,
    save_steps=200,
    save_total_limit=2,
    fp16=True,
    optim="paged_adamw_8bit",
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LEN,
    tokenizer=tokenizer,
)

print("Début de l'entraînement LoRA...")
trainer.train()
print("Entraînement terminé !")

# ==============================================================
# CELLULE 8 — Sauvegarde
# ==============================================================
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Modèle sauvegardé dans : {OUTPUT_DIR}")

# ==============================================================
# CELLULE 9 — Tests du modèle fine-tuné
# ==============================================================
model.eval()
test_questions = [
    "I have had a headache and fever for 3 days. What should I do?",
    "What are the main symptoms of type 2 diabetes?",
    "I feel chest pain when I exercise. Is it serious?",
]

print("\n--- Tests du modèle médical ---")
for q in test_questions:
    prompt = f"<|user|>\n{q}<|end|>\n<|assistant|>\n"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=200, temperature=0.7,
            do_sample=True, pad_token_id=tokenizer.eos_token_id,
        )
    resp = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    print(f"\nQ: {q}\nR: {resp}\n{'-'*40}")
