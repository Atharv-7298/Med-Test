import re
import torch
from transformers import pipeline as hf_pipeline

# Decide device
device = 0 if torch.cuda.is_available() else -1
print("Summarizer device:", "GPU" if device == 0 else "CPU")

# Load FLAN-T5 summarization model
summarizer = hf_pipeline(
    "summarization",
    model="google/flan-t5-large",
    tokenizer="google/flan-t5-large",
    device=device,
)

def clean_text(text: str) -> str:
    """
    Remove diarization tags like [Doctor], [Patient], extra spaces, etc.
    """
    text = re.sub(r"\[.*?\]\s*", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def summarize_conversation(conversation: str) -> str:
    """
    Takes full conversation text and returns a concise clinical summary.
    """
    conversation = clean_text(conversation)

    prompt = (
        "Summarize this doctor-patient conversation into a concise clinical summary "
        "focusing on disease, symptoms, medications, and advice:\n\n"
        + conversation
    )

    result = summarizer(
        prompt,
        max_length=180,
        min_length=60,
        do_sample=False,
    )[0]["summary_text"]

    return result.strip()
