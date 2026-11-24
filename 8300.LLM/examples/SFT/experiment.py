"""QLoRA アダプターを学習し、共通テストでの評価や単問への回答生成を行う。"""
import argparse
import json
from collections import Counter
from pathlib import Path
from time import perf_counter

from generate_data import CONDITIONS, DATA, INSTRUCTION, SEED, read_jsonl, write_jsonl
from score import score

MODEL = "unsloth/Qwen2.5-1.5B-Instruct-unsloth-bnb-4bit"
MAX_LENGTH = 384
EPOCHS = 3
ACCUMULATION = 8
LEARNING_RATE = 2e-4
GENERATION = {"do_sample": False, "max_new_tokens": 192, "batch_size": 8}


def write_json(path, value):
    """値を整形した UTF-8 の JSON ファイルに保存する。"""
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def tokenize(row, tokenizer):
    """チャットをトークン化し、長さと回答の復元を確認して質問側を損失計算から除外する。"""
    prompt = tokenizer.apply_chat_template(
        row["messages"][:-1], tokenize=False, add_generation_prompt=True
    )
    full = tokenizer.apply_chat_template(row["messages"], tokenize=False)
    if not full.startswith(prompt):
        raise ValueError("Chat template does not preserve the assistant boundary")
    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
    answer = row["messages"][-1]["content"]
    # Keep the explicit prompt boundary even if a BPE merge could span it.
    completion = tokenizer.encode(full[len(prompt):], add_special_tokens=False)
    ids = prompt_ids + completion
    decoded = tokenizer.decode(completion, skip_special_tokens=True).strip()
    if len(ids) > MAX_LENGTH or decoded != answer:
        raise ValueError(f"Invalid or truncated completion ({len(ids)} tokens): {answer}")
    return {
        "input_ids": ids,
        "attention_mask": [1] * len(ids),
        "labels": [-100] * len(prompt_ids) + completion,
    }


def train(model, tokenizer, condition, output, fast_model, torch):
    """指定条件のアダプターを学習し、検証損失で選んだ重みと計測結果を保存する。"""
    from datasets import Dataset
    from transformers import DataCollatorForSeq2Seq, TrainerCallback
    from trl import SFTConfig, SFTTrainer

    model = fast_model.get_peft_model(
        model, r=16, lora_alpha=16, lora_dropout=0, bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        use_gradient_checkpointing="unsloth", random_state=SEED,
    )
    datasets = {
        split: Dataset.from_list([
            tokenize(row, tokenizer)
            for row in read_jsonl(DATA / f"{split}_{condition}.jsonl")
        ])
        for split in ("train", "validation")
    }

    class CountingTrainer(SFTTrainer):
        """学習中にモデルへ入力したトークン数を集計する SFTTrainer。"""
        tokens = 0

        def compute_loss(self, model, inputs, *args, **kwargs):
            """学習バッチの入力トークン数を加算してから、損失を計算する。"""
            if model.training:
                # Per-device batch size is one, so the collator adds no padding.
                self.tokens += inputs["input_ids"].numel()
            return super().compute_loss(model, inputs, *args, **kwargs)

    benchmark = {}

    class Throughput(TrainerCallback):
        """指定した学習ステップの時刻と累積トークン数を記録する。"""
        def on_step_end(self, args, state, control, **kwargs):
            """ステップ10と35の終了時に GPU を同期し、処理速度の計測点を記録する。"""
            if state.global_step in (10, 35):
                torch.cuda.synchronize()
                benchmark[state.global_step] = (perf_counter(), trainer.tokens)

    bf16 = torch.cuda.is_bf16_supported()
    config = SFTConfig(
        output_dir=str(output / "checkpoints"),
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=ACCUMULATION,
        learning_rate=LEARNING_RATE,
        warmup_steps=10,
        optim="adamw_8bit",
        seed=SEED,
        data_seed=SEED,
        fp16=not bf16,
        bf16=bf16,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        logging_steps=10,
        report_to="none",
        max_length=MAX_LENGTH,
        dataset_kwargs={"skip_prepare_dataset": True},
    )
    trainer = CountingTrainer(
        model=model, processing_class=tokenizer,
        args=config, train_dataset=datasets["train"], eval_dataset=datasets["validation"],
        data_collator=DataCollatorForSeq2Seq(tokenizer, label_pad_token_id=-100),
        callbacks=[Throughput()],
    )
    torch.cuda.synchronize()
    started = perf_counter()
    result = trainer.train()
    torch.cuda.synchronize()
    elapsed = perf_counter() - started

    adapter = output / "adapter"
    trainer.save_model(str(adapter))
    tokenizer.save_pretrained(str(adapter))
    start_time, start_tokens = benchmark[10]
    stop_time, stop_tokens = benchmark[35]
    write_json(output / "training.json", {
        "base_model": MODEL,
        "gpu": torch.cuda.get_device_name(),
        "seed": SEED,
        "epochs": EPOCHS,
        "batch_size": 1,
        "gradient_accumulation_steps": ACCUMULATION,
        "learning_rate": LEARNING_RATE,
        "wall_seconds_including_validation_and_checkpoints": elapsed,
        "training_tokens": trainer.tokens,
        "mean_training_tokens_per_example": (
            sum(len(ids) for ids in datasets["train"]["input_ids"]) / len(datasets["train"])
        ),
        "tokens_per_second_steps_11_to_35": (
            (stop_tokens - start_tokens) / (stop_time - start_time)
        ),
        "best_checkpoint": trainer.state.best_model_checkpoint,
        "trainer_metrics": result.metrics,
        "log_history": trainer.state.log_history,
    })


def generate_responses(model, tokenizer, conversations, torch):
    """会話をまとめて入力し、各会話の新規生成部分を文字列で返す。"""
    tokenizer.padding_side = "left"
    prompts = [
        tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        for messages in conversations
    ]
    inputs = tokenizer(
        prompts, return_tensors="pt", padding=True, add_special_tokens=False
    ).to("cuda")
    with torch.inference_mode():
        generated = model.generate(
            **inputs, do_sample=GENERATION["do_sample"],
            max_new_tokens=GENERATION["max_new_tokens"],
            pad_token_id=tokenizer.pad_token_id,
        )
    return tokenizer.batch_decode(
        generated[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True
    )


def evaluate(model, tokenizer, output, fast_model, torch):
    """共通テストを採点し、個別の回答と問題形式別の集計を保存する。"""
    fast_model.for_inference(model)
    rows = read_jsonl(DATA / "test.jsonl")
    predictions = []
    for start in range(0, len(rows), GENERATION["batch_size"]):
        batch = rows[start:start + GENERATION["batch_size"]]
        completions = generate_responses(
            model, tokenizer, [row["messages"] for row in batch], torch
        )
        for row, response in zip(batch, completions, strict=True):
            predictions.append({**row, "response": response, "score": score(response, row)})

    metrics = {}
    for form in ("overall", "one_side", "both_sides"):
        subset = [p["score"] for p in predictions if form == "overall" or p["form"] == form]
        answers = Counter(p["answer"] for p in subset)
        reasoning = Counter(p["reasoning"] for p in subset)
        steps = Counter(step for p in subset for step in p["steps"])
        metrics[form] = {
            "questions": len(subset),
            "accuracy": answers["correct"] / len(subset),
            **{key: answers[key] for key in ("correct", "incorrect", "unparseable")},
            "reasoning": {key: reasoning[key] for key in (
                "equivalent", "not_equivalent", "unparseable", "no_steps"
            )},
            "steps": {key: steps[key] for key in (
                "equivalent", "not_equivalent", "unparseable"
            )},
        }
    write_jsonl(output / "predictions.jsonl", predictions)
    write_json(output / "evaluation.json", {"generation": GENERATION, "metrics": metrics})


def main():
    """引数に応じてモデルを読み込み、学習・評価・単問への回答生成を実行する。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("train", "evaluate", "answer"))
    parser.add_argument("condition", choices=("baseline", *CONDITIONS))
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--equation", help="Linear equation for the answer action.")
    args = parser.parse_args()
    if args.action == "answer" and not (args.equation or "").strip():
        parser.error("answer requires --equation")
    if args.action != "answer" and args.equation is not None:
        parser.error("--equation is only supported for answer")
    if args.action == "train" and args.condition == "baseline":
        parser.error("baseline supports evaluate and answer")

    # Import Unsloth first so it can patch Transformers and TRL.
    from unsloth import FastLanguageModel
    import torch
    from transformers import set_seed

    if not torch.cuda.is_available():
        raise RuntimeError("This experiment requires a CUDA GPU")
    set_seed(SEED)
    output = args.run_directory / args.condition
    if args.action != "answer":
        output.mkdir(parents=True, exist_ok=True)
    model_path = MODEL
    if args.action != "train" and args.condition != "baseline":
        adapter = output / "adapter"
        if not (adapter / "adapter_config.json").is_file():
            raise FileNotFoundError(adapter / "adapter_config.json")
        model_path = str(adapter)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_path,
        max_seq_length=MAX_LENGTH,
        load_in_4bit=True,
    )
    if args.action == "train":
        train(model, tokenizer, args.condition, output, FastLanguageModel, torch)
    elif args.action == "evaluate":
        evaluate(model, tokenizer, output, FastLanguageModel, torch)
    else:
        FastLanguageModel.for_inference(model)
        equation = args.equation.strip().removesuffix(".")
        question = f"Solve for x: {equation}.\n{INSTRUCTION}"
        conversation = [{"role": "user", "content": question}]
        print(generate_responses(model, tokenizer, [conversation], torch)[0].strip())


if __name__ == "__main__":
    main()
