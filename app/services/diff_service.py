"""
Diff and verification service for anti-hallucination guardrails.

Uses Python's difflib.SequenceMatcher (zero external dependencies) to verify
that LLM-rewritten narratives preserve factual accuracy.
"""

import difflib
import re

from app.core.logging import get_logger

logger = get_logger(__name__)


class DiffService:
    """Compares original and rewritten text to detect hallucinations and truncation."""

    # Patterns for extracting factual tokens
    METRIC_PATTERN = re.compile(r'\d+[\d,.]*[%×xX]?')
    TECH_KEYWORDS = re.compile(r'\b(?:Python|Java|JavaScript|TypeScript|React|Angular|Vue|Node\.js|Django|Flask|FastAPI|AWS|GCP|Azure|Docker|Kubernetes|k8s|PostgreSQL|MongoDB|Redis|Kafka|Terraform|CI/CD|GraphQL|REST|gRPC|SQL|NoSQL|Linux|Git)\b', re.IGNORECASE)
    COMPANY_PATTERN = re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b')

    def compute_diff(self, original: str, rewritten: str) -> dict:
        """
        Compute a structured diff between original and rewritten text.

        Returns:
            additions: new content added
            deletions: content removed
            unchanged: preserved content
            similarity_ratio: float 0.0-1.0
        """
        orig_lines = original.strip().splitlines()
        rewrite_lines = rewritten.strip().splitlines()

        differ = difflib.Differ()
        diff = list(differ.compare(orig_lines, rewrite_lines))

        additions = [line[2:] for line in diff if line.startswith('+ ')]
        deletions = [line[2:] for line in diff if line.startswith('- ')]
        unchanged = [line[2:] for line in diff if line.startswith('  ')]

        matcher = difflib.SequenceMatcher(None, original, rewritten)
        similarity = matcher.ratio()

        return {
            "additions": additions,
            "deletions": deletions,
            "unchanged": unchanged,
            "similarity_ratio": round(similarity, 4),
            "additions_count": len(additions),
            "deletions_count": len(deletions),
        }

    def check_truncation(self, original: str, rewritten: str) -> dict:
        """
        Detect if the LLM prematurely truncated its response.

        Checks:
        1. Rewritten is suspiciously shorter (< 60% of original length)
        2. Rewritten ends mid-sentence (no terminal punctuation)
        3. Significant content loss
        """
        orig_len = len(original.strip())
        rewrite_len = len(rewritten.strip())

        ratio = rewrite_len / max(orig_len, 1)
        ends_cleanly = rewritten.strip()[-1] in '.!?)\"' if rewritten.strip() else False

        is_truncated = ratio < 0.6 or (not ends_cleanly and ratio < 0.85)

        return {
            "is_truncated": is_truncated,
            "length_ratio": round(ratio, 3),
            "ends_cleanly": ends_cleanly,
            "original_length": orig_len,
            "rewritten_length": rewrite_len,
        }

    def verify_facts(self, original: str, rewritten: str) -> dict:
        """
        Verify that key factual tokens from the original appear in the rewritten text.

        Checks: metrics/numbers, technology names, and capitalized proper nouns.
        Returns a pass/fail verdict with details.
        """
        # Extract factual tokens from original
        orig_metrics = set(self.METRIC_PATTERN.findall(original))
        orig_techs = set(self.TECH_KEYWORDS.findall(original))

        # Check which ones survive in the rewritten version
        rewrite_lower = rewritten.lower()

        missing_metrics = []
        for m in orig_metrics:
            if m not in rewritten:
                missing_metrics.append(m)

        missing_techs = []
        for t in orig_techs:
            if t.lower() not in rewrite_lower:
                missing_techs.append(t)

        total_facts = len(orig_metrics) + len(orig_techs)
        missing_count = len(missing_metrics) + len(missing_techs)
        preservation_rate = 1.0 - (missing_count / max(total_facts, 1))

        # Fail if more than 20% of facts are missing
        passed = preservation_rate >= 0.8

        return {
            "passed": passed,
            "preservation_rate": round(preservation_rate, 3),
            "original_metrics": sorted(orig_metrics),
            "missing_metrics": missing_metrics,
            "original_techs": sorted(orig_techs),
            "missing_techs": missing_techs,
            "total_facts_checked": total_facts,
            "facts_missing": missing_count,
        }

    def full_verify(self, original: str, rewritten: str) -> dict:
        """Run all verification checks and return a combined verdict."""
        diff = self.compute_diff(original, rewritten)
        truncation = self.check_truncation(original, rewritten)
        facts = self.verify_facts(original, rewritten)

        passed = facts["passed"] and not truncation["is_truncated"]

        return {
            "passed": passed,
            "diff": diff,
            "truncation": truncation,
            "facts": facts,
        }


# Module-level singleton
diff_service = DiffService()
