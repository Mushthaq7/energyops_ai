"""
LoRA Fine-tuning Script for Mistral 7B on Renewable Energy Operations

This script uses the PEFT library to perform parameter-efficient fine-tuning
using LoRA (Low-Rank Adaptation) on a small instruction dataset.

Requirements:
    pip install peft transformers datasets accelerate bitsandbytes trl

Usage:
    python finetune_lora.py

Note: This script requires a GPU with at least 16GB VRAM for QLoRA (4-bit quantization).
      For CPU-only or smaller GPUs, reduce batch size or use a smaller model.
"""

import os
import json
import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType,
)
from trl import SFTTrainer

# ============================================================================
# Configuration
# ============================================================================

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"
DATASET_PATH = "data/energy_instructions.json"
OUTPUT_DIR = "./lora_output"

# LoRA Configuration
LORA_R = 16              # LoRA rank
LORA_ALPHA = 32          # LoRA alpha (scaling factor)
LORA_DROPOUT = 0.05      # LoRA dropout
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj"]  # Attention layers

# Training Configuration
MAX_SEQ_LENGTH = 512
BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 4
NUM_EPOCHS = 3
LEARNING_RATE = 2e-4
WARMUP_RATIO = 0.03

# ============================================================================
# Helper Functions
# ============================================================================

def load_dataset_from_json(path: str) -> Dataset:
    """Load instruction dataset from JSON file."""
    with open(path, "r") as f:
        data = json.load(f)
    return Dataset.from_list(data)

def format_instruction(sample: dict) -> str:
    """Format instruction sample into prompt format for Mistral."""
    instruction = sample.get("instruction", "")
    input_text = sample.get("input", "")
    output = sample.get("output", "")
    
    if input_text:
        prompt = f"""<s>[INST] {instruction}

Input: {input_text} [/INST] {output}</s>"""
    else:
        prompt = f"""<s>[INST] {instruction} [/INST] {output}</s>"""
    
    return prompt

def formatting_prompts_func(examples):
    """Format examples for SFTTrainer."""
    texts = []
    for i in range(len(examples["instruction"])):
        sample = {
            "instruction": examples["instruction"][i],
            "input": examples["input"][i],
            "output": examples["output"][i],
        }
        texts.append(format_instruction(sample))
    return {"text": texts}

# ============================================================================
# Main Fine-tuning Logic
# ============================================================================

def main():
    print("=" * 60)
    print("LoRA Fine-tuning: Mistral 7B for Energy Operations")
    print("=" * 60)
    
    # Check for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    if device == "cpu":
        print("WARNING: Training on CPU will be very slow. GPU recommended.")
        use_4bit = False
    else:
        use_4bit = True
    
    # Load dataset
    print(f"\nLoading dataset from {DATASET_PATH}...")
    dataset = load_dataset_from_json(DATASET_PATH)
    dataset = dataset.map(
        lambda x: {"text": format_instruction(x)},
        remove_columns=dataset.column_names
    )
    print(f"Loaded {len(dataset)} samples")
    
    # Quantization config (4-bit for memory efficiency)
    if use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
    else:
        bnb_config = None
    
    # Load tokenizer
    print(f"\nLoading tokenizer: {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # Load model
    print(f"Loading model: {MODEL_NAME}...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto" if use_4bit else None,
        trust_remote_code=True,
    )
    
    if use_4bit:
        model = prepare_model_for_kbit_training(model)
    
    # LoRA Configuration
    print("\nConfiguring LoRA...")
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Initialize Trainer
    print("\nInitializing SFTTrainer...")

    from trl import SFTConfig
    sft_config = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        warmup_ratio=WARMUP_RATIO,
        logging_steps=10,
        save_strategy="epoch",
        fp16=use_4bit,
        optim="paged_adamw_8bit" if use_4bit else "adamw_torch",
        report_to="none",
        max_seq_length=MAX_SEQ_LENGTH,
        dataset_text_field="text",
        packing=False,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        args=sft_config,
        processing_class=tokenizer,
    )
    
    # Train
    print("\nStarting fine-tuning...")
    print("-" * 60)
    trainer.train()
    
    # Save the LoRA adapter
    print(f"\nSaving LoRA adapter to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print("\n" + "=" * 60)
    print("Fine-tuning complete!")
    print(f"LoRA adapter saved to: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
