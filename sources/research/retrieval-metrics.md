# Retrieval evaluation metrics

Hit@k is one when at least one relevant source appears among the top k retrieved passages, otherwise zero. Mean reciprocal rank (MRR) averages the inverse rank of the first relevant retrieved source across queries. These are retrieval metrics, not measures of language model factuality or citation faithfulness.

A sound benchmark defines relevant sources independently of the retrieval output and reports the number of queries, the evaluation split and the retrieval configuration. A tiny synthetic benchmark is a smoke test, not evidence of state-of-the-art performance.