# Kazakh Text Cleaning and Spam Datasets

This repository contains the data-cleaning pipeline and dataset artifacts used to prepare two Kazakh-language Hugging Face datasets:

- [`salyamq/kazspam-v1`](https://huggingface.co/datasets/salyamq/kazspam-v1) — a dataset for spam and unwanted-content classification;
- [`salyamq/kk-corpus-v1`](https://huggingface.co/datasets/salyamq/kk-corpus-v1) — a cleaned corpus for Kazakh NLP and language-model pretraining.


### KazSpam v1

`KazSpam v1` contains 10,000 web-crawled documents automatically classified into four categories:

| Label | Description | Examples |
|---|---|---:|
| `normal` | Ordinary useful or neutral text | 1,460 |
| `casino` | Gambling, casino, betting, and bookmaker content | 7,071 |
| `porn` | Adult and explicit content | 1,424 |
| `other` | Other advertising, promotional, or unwanted content | 45 |

The source documents come from multilingual web corpora, including CC100, CulturaX, HPLT, MADLAD-400, mC4, OSCAR, Kazakh Books, Kazakh News, and Wikipedia.

### Kazakh Corpus v1

`Kazakh Corpus v1` is a cleaned corpus assembled from books, news, Wikipedia, and web-crawled sources.

| Metric | Value |
|---|---:|
| Original documents | 6,381,508 |
| Removed as spam | 57,950 |
| Removed as corrupted | 534 |
| Retained documents | 6,323,024 |
| Characters before cleaning | 19,296,026,576 |
| Characters after cleaning | 19,249,762,916 |


## Cleaning Pipeline

The first-stage cleaning pipeline performs the following operations:

1. Decodes escaped line breaks, tabs, carriage returns, and common HTML entities.
2. Removes paragraphs containing corrupted replacement characters.
3. Removes empty paragraphs.
4. Normalizes mixed Cyrillic and Latin homoglyphs.
5. Collapses excessive repeated punctuation.
6. Removes HTML tags and invisible Unicode characters.
7. Applies Unicode NFC normalization and whitespace cleanup.
8. Filters documents that match spam heuristics.

## Spam Detection

The spam filter uses keyword and emoji-ratio heuristics to detect common gambling and adult-content patterns. The classifier used for `KazSpam v1` assigns each document to one of four categories: `normal`, `casino`, `porn`, or `other`.

## Data Quality Notes

The source data is heterogeneous and may contain machine-translated text, Russian or English fragments, web boilerplate, duplicated passages, SEO content, OCR artifacts, truncated documents, and residual unwanted content.

The cleaning pipeline is heuristic-based. It can produce both false positives and false negatives, so additional language identification, deduplication, quality filtering, and manual review are recommended for production use.

## Reproducibility and Safety

- Do not commit API keys or other credentials to the repository.
- The automatic classifier uses an OpenAI-compatible API endpoint through OpenRouter.
- The original source datasets may have different licenses and usage restrictions.
- Review the license and redistribution terms of every source before using the combined corpus commercially.

## License

This repository combines code and data derived from multiple sources. The code and each dataset may be subject to different licenses. No single license should be assumed for the complete repository; check the terms of the relevant source dataset before redistribution or commercial use.
