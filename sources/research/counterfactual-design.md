# Counterfactual evaluation protocol

A controlled evidence intervention keeps the user question fixed and removes or replaces one supporting passage. The evaluator should specify the expected behavior before observing the answer. Replacing a refund policy with a different number should update the answer when the policy is relevant. Removing the policy should cause abstention when no alternative policy remains.

A negative control removes irrelevant evidence while retaining the relevant source. The answer should often remain stable. Repeated trials are needed when model generation is stochastic, and an observed answer change alone is not proof of causal dependence.