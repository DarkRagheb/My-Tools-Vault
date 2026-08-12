"""pytest configuration and test-time shims for TorBot tests.

This module provides a lightweight stub for the NLP classifier so tests can
run without installing the full scientific stack (numpy, scikit-learn, etc.).
The stub is only active during test runs and does not affect production code.
"""
import sys
import types


def _install_nlp_stub():
    """Install a minimal stub for torbot.modules.nlp.main during tests."""
    mod_name = "torbot.modules.nlp.main"
    if mod_name in sys.modules:
        return

    # Create a minimal module with classify function
    stub = types.ModuleType(mod_name)

    def classify(data):
        """Lightweight test-only classifier.

        Returns a deterministic classification without requiring ML libraries.
        Real implementation uses sklearn pipeline with training data.
        """
        _ = data  # unused in stub
        return ["unknown", 0.0]

    # Use setattr to avoid linter complaints about dynamic attributes
    setattr(stub, "classify", classify)
    sys.modules[mod_name] = stub


# Install stub before any test imports
_install_nlp_stub()
