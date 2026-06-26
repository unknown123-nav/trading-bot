FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    libgomp1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download FinBERT once while building the image
RUN python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert'); \
model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); \
tokenizer.save_pretrained('/app/finbert'); \
model.save_pretrained('/app/finbert')"
COPY . .

CMD ["python", "main.py"]
