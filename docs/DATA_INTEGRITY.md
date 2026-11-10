# DATA INTEGRITY methodology

EvidenceFlip separates two questions:

1. **Source-file integrity:** Does a source match the SHA-256 fingerprint registered for it?
2. **Evidence sensitivity:** Does an AI answer respond appropriately to controlled changes in supplied evidence?

## Procedure

- Register each document with an ID, path, provenance, license, and SHA-256 hash.
- Verify the bytes of the source before testing.
- Establish a baseline answer using the original document set.
- Replace or remove one source at a time while holding the question fixed.
- Include a negative control that removes an unrelated source.
- Check predefined assertions, answer changes, and whether citations refer to supplied source IDs.
- Preserve the test results for audit and human review.

## Limitations

Hash matching does not prove that a source is factually true. A valid citation ID does not prove claim-level support. An answer changing does not by itself establish causal dependence. Synthetic fixtures are not AI training data.