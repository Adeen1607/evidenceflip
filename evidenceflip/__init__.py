"""EvidenceFlip: DATA INTEGRITY evaluation for retrieval-augmented AI."""
from .core import Evidence, Answer, Scenario, Evaluation, evaluate, verify_registry
__all__ = ["Evidence", "Answer", "Scenario", "Evaluation", "evaluate", "verify_registry"]
__version__ = "0.2.0"
