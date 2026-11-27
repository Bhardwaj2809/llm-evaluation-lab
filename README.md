# LLM Evaluation Lab

A small Python project for evaluating answers from a local language model. It generates answers to AWS questions, scores them with an LLM judge, and can extract and classify individual factual claims against reference answers.

## Requirements

- Python 3.10 or later
- [Ollama](https://ollama.com/) installed and running
- The `gemma3:4b` model (the model is configured in `src/llm.py`)

## Setup

Run these commands from the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
ollama pull gemma3:4b
```

## Run

Generate answers from `dataset/questions.json`:

```powershell
python src\generate.py
```

Evaluate the generated answers against their reference answers:

```powershell
python src\evaluate.py
```

Extract claims from generated answers and classify them using only the reference answers as evidence:

```powershell
python src\verify_claims.py
```

Compare claim classifications with the human labels:

```powershell
python src\compare.py
```

The scripts write their outputs to `results/`. Run them from the project directory so the relative dataset and result paths resolve correctly. The comparison script expects `results/claim_evaluations.json`, which is produced by `src/verify_claims.py`.

## Project layout

- `dataset/` — sample questions and human evaluation labels
- `src/` — answer generation, answer evaluation, claim extraction, and comparison scripts
- `results/` — sample outputs and generated evaluation results
- `requirements.txt` — Python dependencies

LLM judge outputs can be inconsistent; treat the result files as experimental outputs rather than authoritative evaluations.
