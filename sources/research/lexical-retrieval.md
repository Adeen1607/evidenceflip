# Lexical retrieval notes

BM25 is a lexical ranking method that weighs query term frequency and corpus document frequency while normalizing for passage length. It can provide an interpretable and inexpensive baseline without GPUs or hosted embeddings. Its lexical matching cannot reliably discover paraphrases with no shared terms.

Dense vector retrieval uses an embedding model to map questions and passages into a representation space. Comparing lexical and dense retrieval on the same evaluation split is a useful future experiment, rather than proof that one method always wins.