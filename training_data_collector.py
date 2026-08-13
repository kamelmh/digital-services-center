"""Training Data Collector — Save all generator inputs/outputs for improvement.

Stores structured data for:
- Prompt optimization
- Quality scoring
- Market analysis
- Model fine-tuning (eventual)
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TrainingDataCollector:
    """Collect and store training data from all generators."""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "training_data")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.index_file = self.data_dir / "index.jsonl"
        self._ensure_index()

    def _ensure_index(self):
        if not self.index_file.exists():
            self.index_file.write_text("", encoding="utf-8")

    def _hash_input(self, data: dict) -> str:
        """Create a deterministic hash of input parameters."""
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:12]

    def save_generation(
        self,
        generator: str,
        input_params: dict,
        output_content: str,
        provider: str = None,
        model: str = None,
        quality_score: float = None,
        compliance_score: float = None,
        metadata: dict = None,
    ) -> str:
        """Save a generation record.
        
        Returns the record ID.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        input_hash = self._hash_input(input_params)

        record = {
            "id": f"gen_{timestamp[:10]}_{input_hash}",
            "timestamp": timestamp,
            "generator": generator,
            "input": input_params,
            "input_hash": input_hash,
            "output": {
                "content": output_content,
                "word_count": len(output_content.split()),
                "char_count": len(output_content),
            },
            "provider": provider,
            "model": model,
            "quality_score": quality_score,
            "compliance_score": compliance_score,
            "metadata": metadata or {},
        }

        # Save individual record
        record_file = self.data_dir / f"{record['id']}.json"
        record_file.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

        # Append to index
        index_entry = {
            "id": record["id"],
            "timestamp": timestamp,
            "generator": generator,
            "input_hash": input_hash,
            "word_count": record["output"]["word_count"],
            "provider": provider,
        }
        with open(self.index_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")

        return record["id"]

    def load_records(self, generator: str = None, limit: int = 100) -> list[dict]:
        """Load records, optionally filtered by generator."""
        records = []
        if not self.index_file.exists():
            return records

        with open(self.index_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if generator and entry.get("generator") != generator:
                    continue
                records.append(entry)
                if len(records) >= limit:
                    break
        return records

    def get_stats(self) -> dict:
        """Get statistics about collected training data."""
        stats = {
            "total_records": 0,
            "by_generator": {},
            "by_provider": {},
            "avg_word_count": 0,
            "date_range": {"first": None, "last": None},
        }

        if not self.index_file.exists():
            return stats

        total_words = 0
        dates = []

        with open(self.index_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                stats["total_records"] += 1

                gen = entry.get("generator", "unknown")
                stats["by_generator"][gen] = stats["by_generator"].get(gen, 0) + 1

                prov = entry.get("provider", "unknown")
                stats["by_provider"][prov] = stats["by_provider"].get(prov, 0) + 1

                total_words += entry.get("word_count", 0)
                dates.append(entry.get("timestamp", ""))

        if stats["total_records"] > 0:
            stats["avg_word_count"] = total_words // stats["total_records"]
        if dates:
            dates.sort()
            stats["date_range"]["first"] = dates[0]
            stats["date_range"]["last"] = dates[-1]

        return stats

    def find_duplicates(self) -> list[dict]:
        """Find duplicate inputs (same hash, different outputs)."""
        hash_map = {}
        if not self.index_file.exists():
            return []

        with open(self.index_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                h = entry.get("input_hash", "")
                if h not in hash_map:
                    hash_map[h] = []
                hash_map[h].append(entry)

        duplicates = []
        for h, entries in hash_map.items():
            if len(entries) > 1:
                duplicates.append({
                    "input_hash": h,
                    "count": len(entries),
                    "records": [e["id"] for e in entries],
                    "generators": list(set(e.get("generator", "") for e in entries)),
                })

        return duplicates

    def export_for_finetuning(self, output_file: str = None) -> str:
        """Export data in format suitable for model fine-tuning."""
        if output_file is None:
            output_file = str(self.data_dir / "finetuning_export.jsonl")

        records = []
        if not self.index_file.exists():
            return output_file

        with open(self.index_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                record_file = self.data_dir / f"{entry['id']}.json"
                if record_file.exists():
                    full = json.loads(record_file.read_text(encoding="utf-8"))
                    records.append({
                        "input": json.dumps(full["input"], ensure_ascii=False),
                        "output": full["output"]["content"],
                        "generator": full["generator"],
                    })

        with open(output_file, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        return output_file


if __name__ == "__main__":
    collector = TrainingDataCollector()

    record_id = collector.save_generation(
        generator="feasibility",
        input_params={
            "business_type": "quincaillerie",
            "wilaya": "El Bayadh",
            "investment": 4_600_000,
            "business_name": "DSC Test",
        },
        output_content="Test generation for training data...",
        provider="groq",
        model="llama-3.3-70b",
    )
    print(f"Saved record: {record_id}")

    stats = collector.get_stats()
    print(f"Total records: {stats['total_records']}")
    print(f"By generator: {stats['by_generator']}")
