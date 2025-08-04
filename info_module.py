# info_module.py

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import ddg
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

import traceback


def search_web(query, num_results=3):
    try:
        results = ddg(query, max_results=num_results)
        links = [r['href'] for r in results if 'href' in r and r['href'].startswith("http")]
        if not links:
            raise Exception("No links found.")
        return links
    except Exception as e:
        print("Search Error:", e)
        traceback.print_exc()
        return []


def extract_text(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            raise Exception(f"Non-200 response: {res.status_code}")
        soup = BeautifulSoup(res.text, 'html.parser')
        paras = soup.find_all('p')
        if not paras:
            raise Exception("No <p> tags found.")
        text = ' '.join(p.get_text(strip=True) for p in paras)
        if len(text) < 100:
            raise Exception("Extracted text too short.")
        return text
    except Exception as e:
        print(f"[ERROR] Failed to extract from {url}: {e}")
        return ""


def summarize_text(text, sentence_count=4):
    try:
        if len(text.split()) < 50:
            return text  # Text too short to summarize, return as-is
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = TextRankSummarizer()
        summary = summarizer(parser.document, sentence_count)
        output = ' '.join(str(sentence) for sentence in summary)
        if not output:
            raise Exception("Summary returned empty.")
        return output
    except Exception as e:
        print(f"[ERROR] Summarization failed: {e}")
        return text[:300] + "..."  # Fallback: first 300 chars


def confirm_facts(summary_list):
    try:
        all_sentences = ' '.join(summary_list).split('. ')
        fact_freq = {}
        for sentence in all_sentences:
            sentence = sentence.strip()
            if len(sentence) < 25:
                continue
            fact_freq[sentence] = fact_freq.get(sentence, 0) + 1
        if not fact_freq:
            raise Exception("No facts to confirm.")
        sorted_facts = sorted(fact_freq.items(), key=lambda x: x[1], reverse=True)
        return '. '.join([f[0] for f in sorted_facts[:3]]) + '.'
    except Exception as e:
        print("[WARN] Fact confirmation failed:", e)
        return ' '.join(summary_list[:2]) + '.'


def info_pipeline(query):
    try:
        print(f"[INFO] Query received: {query}")
        urls = search_web(query)
        if not urls:
            return {
                "answer": "I couldn't find any relevant sources for this topic. Please try rephrasing.",
                "sources": []
            }

        raw_texts = []
        for url in urls:
            text = extract_text(url)
            if text:
                raw_texts.append(text)
            else:
                print(f"[WARN] Skipped empty text from {url}")

        if not raw_texts:
            return {
                "answer": "No valid content could be extracted from the search results.",
                "sources": urls
            }

        summaries = [summarize_text(t) for t in raw_texts]
        final_answer = confirm_facts(summaries)

        return {
            "answer": final_answer.strip(),
            "sources": urls
        }

    except Exception as e:
        print("[CRITICAL] info_pipeline failed:", e)
        traceback.print_exc()
        return {
            "answer": "An unexpected error occurred. Sanji AI's brain just faceplanted. Try again later.",
            "sources": []
        }