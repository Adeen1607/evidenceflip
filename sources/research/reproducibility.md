# Reproducibility checklist

For a reproducible retrieval-augmented generation experiment, record the evaluation question set, dataset revision, source file digests, document chunk size, chunk overlap, retrieval algorithm and its parameters, generation model identifier, decoding parameters and prompt template. When a model supports seeds, record the seed. A seed alone cannot guarantee determinism on every hardware and software configuration.

Results should identify whether they were obtained using a deterministic reference adapter, a locally running language model, or a remote language model. Do not describe a simulated example as a real model evaluation.