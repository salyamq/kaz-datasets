# LLM Valuation Summary — Kazakh Pretraining Corpus

1. **Script Mixing & Alphabet Inconsistency** — Pervasive Latin-character intrusion into Cyrillic Kazakh text (e.g. visually confusable characters like "a"/"а", "e"/"е", "o"/"о") and inconsistent switching between Latin and Cyrillic scripts within a single document. This corrupts tokenization and degrades model output quality.

2. **Machine Translation Artifacts & Unnatural Language** — Large portions of the corpus exhibit clear signs of algorithmic/literal translation: awkward phrasing, incorrect case/gender agreement, calendar/date errors (wrong month-day correspondences), factual inaccuracies, and essay-mill content. These degrade the model's grasp of natural Kazakh syntax and semantics.

3. **Structural Corruption & Web Boilerplate** — Documents are riddled with residual HTML tags/entities, embedded URLs, literal escape sequences (`\n`), invisible Unicode characters (zero-width spaces, control chars), OCR/PDF export damage, and SEO keyword stuffing. Truncated and concatenated documents further fragment meaning.

4. **Data Duplication & Redundancy** — Exact duplicated paragraphs, repeated near-identical documents, and copy-pasted content appear throughout the corpus. This inflates training data, biases the model toward repeated patterns, and wastes compute.

5. **Harmful, Spam & Off-Topic Content** — The corpus contains adult/explicit material, casino and medical spam, classified ads, personal pages, and non-Kazakh/Russian-language insertions. These are irrelevant to pretraining objectives and risk producing unsafe or off-topic model outputs.
