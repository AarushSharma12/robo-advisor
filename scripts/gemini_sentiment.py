from __future__ import annotations

import argparse
import json
import os
from typing import Dict, List, Literal, Optional

try:
  import google.generativeai as genai
except Exception:
  genai = None

Sentiment = Literal['Positive', 'Negative', 'Neutral']
EntityType = Literal["Company", "Sector"]

class GeminiArticleSentimentExtractor:
  """
    Extracts per-entity sentiment from plain-text news articles using Google Gemini.
  """

  def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, api_key_file: Optional[str] = None, env_file: Optional[str] = None) -> None:
    self._load_env_file(env_file)

    file_key = self._read_api_key_file(api_key_file)
    self._api_key = api_key or os.getenv("GOOGLE_API_KEY") or file_key
    self._model_name = model or os.getenv("GOOGLE_GEMINI_MODEL", "gemini-1.5-flash")
    self._enabled = bool(self._api_key and genai is not None)
    self._model = None
    if self._enabled:
      genai.configure(api_key=self._api_key)
      try:
        self._model = genai.GenerativeModel(
          model_name=self._model_name,
          generation_config={
            "temperature": 0.0,
            "response_mime_type": "application/json",
          },
        )
      except TypeError:
        self._model = genai.GenerativeModel(
          model=self._model_name,
          generation_config={
            "temperature": 0.0,
            "response_mime_type": "application/json",
          },
        )

  def _repo_root(self) -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

  def _default_env_file_path(self) -> str:
    return os.path.join(self._repo_root(), ".env")

  def _load_env_file(self, path: Optional[str]) -> None:
    env_path = path or os.getenv("GOOGLE_API_ENV_FILE") or self._default_env_file_path()
    try:
      with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
          s = line.strip()
          if not s or s.startswith("#"):
            continue
          if "=" not in s:
            continue
          k, v = s.split("=", 1)
          k = k.strip()
          v = v.strip().strip('"').strip("'")
          if k and (k not in os.environ):
            os.environ[k] = v
    except Exception:
      pass

  def _read_api_key_file(self, path: Optional[str]) -> Optional[str]:
    candidate = path or os.getenv("GOOGLE_API_KEY_FILE")
    if not candidate:
      return None
    try:
      with open(candidate, "r", encoding="utf-8") as f:
        key = f.read().strip()
        return key or None
    except Exception:
      return None

  def extract_sentiment(self, text: str) -> List[Dict[str, str]]:
    if not self._enabled or not self._model or not text:
      return []
    prompt = f"""
    You are a financial NLP assistant. From the following article, extract all referenced entities that are either:
    - Company (publicly traded); output the stock ticker symbol as the name (e.g., AAPL, MSFT).
    - Sector (GICS-like); output the sector name as the name (e.g., Technology, Energy). Sector names may include the word "Sector" (e.g., "Energy Sector").

    Guidance:
    - Symbols often appear in parentheses after the company name (e.g., Enbridge (ENB)); when present, use that ticker for the Company name.
    - Output exactly ONE entry per unique entity. If an entity is mentioned multiple times with mixed tones, choose the majority sentiment; on ties, choose "Neutral".

    For each extracted entity, assign a sentiment strictly as "Positive", "Negative", or "Neutral" based ONLY on the article's content and short-term price impact.
    Skip entities if ambiguous or not clearly mentioned in a market-moving way.

    Return ONLY a JSON object with this exact shape:
    {{
      "entities": [
        {{ "name": "AAPL", "type": "Company", "sentiment": "Positive" }},
        {{ "name": "Energy Sector", "type": "Sector", "sentiment": "Neutral" }}
      ]
    }}

    Constraints:
    - Keys must be: name, type, sentiment (case-sensitive).
    - type must be "Company" or "Sector" only.
    - sentiment must be "Positive", "Negative", or "Neutral" only.
    - For Company, name must be the STOCK TICKER SYMBOL in uppercase. If you cannot reliably determine the ticker, do NOT include it.
    - For Sector, use standard sector names (e.g., Technology, Energy, Financials, Healthcare, Industrials, Consumer Discretionary, Consumer Staples, Communication Services, Utilities, Materials, Real Estate). Including the suffix "Sector" is acceptable.

    Article:
    {text}
    """.strip()

    try:
      response = self._model.generate_content(prompt)
      raw_output = (response.text or "").strip()
      if not raw_output.startswith("{") and not raw_output.startswith("["):
        start = raw_output.find("{")
        alt_start = raw_output.find("[")
        if start == -1 and alt_start != -1:
          start = alt_start
          end = raw_output.rfind("]")
        else:
          end = raw_output.rfind("}")
        if start != -1 and end != -1:
          raw_output = raw_output[start:end + 1]
      parsed = json.loads(raw_output)
      if isinstance(parsed, dict) and isinstance(parsed.get("entities"), list):
        sentiment_items = parsed["entities"]
      elif isinstance(parsed, list):
        sentiment_items = parsed
      else:
        return []
    except Exception:
      return []

    out: List[Dict[str, str]] = []
    for item in sentiment_items:
      try:
        name = str(item.get("name", "")).strip()
        entity_type = str(item.get("type", "")).strip()
        sentiment = str(item.get("sentiment", "")).strip()
        if entity_type not in ("Company", "Sector"):
          continue
        if sentiment not in ("Positive", "Negative", "Neutral"):
          continue
        if entity_type == "Company":
          if not name or not name.isupper():
            continue
          if not all(c.isalnum() or c in ("-", ".") for c in name):
            continue
        else:
          if not all(c.isalnum() or c in ("-", ".", " ", "&", "/") for c in name):
            continue
        if not name:
          continue
        out.append({"name": name, "type": entity_type, "sentiment": sentiment})
      except Exception:
        continue

    return self._aggregate_entities(out)

  def _aggregate_entities(self, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    from collections import Counter, defaultdict
    stats = defaultdict(Counter)
    order: List[tuple[str, str]] = []
    for it in items:
      key = (it["name"], it["type"])
      if key not in stats:
        order.append(key)
      stats[key][it["sentiment"]] += 1

    result: List[Dict[str, str]] = []
    for name, typ in order:
      counts = stats[(name, typ)]
      pos = counts.get("Positive", 0)
      neg = counts.get("Negative", 0)
      neu = counts.get("Neutral", 0)
      max_count = max(pos, neg, neu)
      winners = [s for s, c in (("Positive", pos), ("Negative", neg), ("Neutral", neu)) if c == max_count and max_count > 0]
      chosen = winners[0] if len(winners) == 1 else "Neutral"
      result.append({"name": name, "type": typ, "sentiment": chosen})
    return result

def _read_text(path: str) -> str:
  with open(path, "r", encoding="utf-8") as f:
    return f.read()

def main():
  parser = argparse.ArgumentParser(description="Extract entity sentiments from an article using Google Gemini.")
  parser.add_argument("-f", "--file", default="data/articles/article1.txt", help="Path to article text file")
  parser.add_argument("--model", default=None, help="Override model name (defaults to env GOOGLE_GEMINI_MODEL or gemini-1.5-flash)")
  parser.add_argument("--key", default=None, help="Override API key (highest precedence)")
  parser.add_argument("--key-file", default=None, help="Path to file containing Google API key (used only if provided or via GOOGLE_API_KEY_FILE)")
  parser.add_argument("--env-file", default=None, help="Path to .env file (defaults to repo-root/.env)")
  args = parser.parse_args()

  text = _read_text(args.file)
  extractor = GeminiArticleSentimentExtractor(model=args.model, api_key=args.key, api_key_file=args.key_file, env_file=args.env_file)
  results = extractor.extract_sentiment(text)
  print(json.dumps({"entities": results}, indent=2))

if __name__ == "__main__":
  main()

