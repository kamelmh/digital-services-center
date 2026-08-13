"""Training Data Hook — Automatically save I/O from every generator.

Import and call hook_generation() after each generation to save:
- Input parameters
- Output content
- Provider/model used
- Timestamp
- Quality metrics (if available)
"""

import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path


class TrainingDataHook:
    """Auto-save generator I/O for training data."""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "training_data")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.index_file = self.data_dir / "index.jsonl"
        if not self.index_file.exists():
            self.index_file.write_text("", encoding="utf-8")

    def _hash_input(self, data: dict) -> str:
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()[:12]

    def save(
        self,
        generator: str,
        input_params: dict,
        output_content: str,
        provider: str = None,
        model: str = None,
        quality_score: float = None,
        metadata: dict = None,
    ) -> str:
        """Save a generation record. Returns record ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        input_hash = self._hash_input(input_params)

        record = {
            "id": f"gen_{timestamp[:10]}_{input_hash}",
            "timestamp": timestamp,
            "generator": generator,
            "input": input_params,
            "input_hash": input_hash,
            "output_len": len(output_content),
            "output_words": len(output_content.split()),
            "provider": provider,
            "model": model,
            "quality_score": quality_score,
            "metadata": metadata or {},
        }

        # Save full record
        record_file = self.data_dir / f"{record['id']}.json"
        record_file.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

        # Append to index
        index_entry = {
            "id": record["id"],
            "ts": timestamp,
            "gen": generator,
            "hash": input_hash,
            "words": record["output_words"],
            "prov": provider,
        }
        with open(self.index_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")

        return record["id"]

    def get_stats(self) -> dict:
        stats = {"total": 0, "by_generator": {}, "by_provider": {}}
        if not self.index_file.exists():
            return stats
        with open(self.index_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                e = json.loads(line)
                stats["total"] += 1
                g = e.get("gen", "unknown")
                stats["by_generator"][g] = stats["by_generator"].get(g, 0) + 1
                p = e.get("prov") or "unknown"
                stats["by_provider"][p] = stats["by_provider"].get(p, 0) + 1
        return stats


# Singleton for easy import
hook = TrainingDataHook()


def hook_generation(generator: str, input_params: dict, output_content: str, **kwargs) -> str:
    """Convenience function — call after every generation."""
    return hook.save(generator, input_params, output_content, **kwargs)
