"""Batch processing for recurring clients — same wilaya, same business type."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

BATCH_DIR = Path(__file__).parent / "batch_orders"
CLIENTS_FILE = BATCH_DIR / "clients.json"
DRAFTS_DIR = BATCH_DIR / "drafts"


@dataclass
class Client:
    id: str
    name: str
    phone: str
    email: str = ""
    wilaya: str = ""
    business_type: str = ""
    investment: int = 0
    service: str = "feasibility"
    status: str = "new"  # new, quoted, in_progress, delivered, paid
    created_at: str = ""
    last_updated: str = ""
    notes: str = ""
    dossiers: list = None  # IDs of generated dossiers
    referrals: int = 0  # how many referrals from this client

    def __post_init__(self):
        if self.dossiers is None:
            self.dossiers = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_updated:
            self.last_updated = self.created_at


class BatchManager:
    def __init__(self):
        BATCH_DIR.mkdir(exist_ok=True)
        DRAFTS_DIR.mkdir(exist_ok=True)
        self.clients = self._load_clients()

    def _load_clients(self) -> dict:
        if CLIENTS_FILE.exists():
            data = json.loads(CLIENTS_FILE.read_text(encoding="utf-8"))
            return {k: Client(**v) for k, v in data.items()}
        return {}

    def _save_clients(self):
        data = {k: asdict(v) for k, v in self.clients.items()}
        CLIENTS_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def add_client(self, name: str, phone: str, wilaya: str, business_type: str,
                   investment: int = 0, service: str = "feasibility", email: str = "",
                   notes: str = "") -> Client:
        client_id = f"client-{len(self.clients)+1:04d}"
        client = Client(
            id=client_id, name=name, phone=phone, email=email,
            wilaya=wilaya, business_type=business_type, investment=investment,
            service=service, notes=notes,
        )
        self.clients[client_id] = client
        self._save_clients()
        return client

    def update_status(self, client_id: str, status: str, notes: str = ""):
        if client_id in self.clients:
            self.clients[client_id].status = status
            self.clients[client_id].last_updated = datetime.now().isoformat()
            if notes:
                self.clients[client_id].notes = notes
            self._save_clients()

    def get_by_wilaya(self, wilaya: str) -> list:
        return [c for c in self.clients.values() if c.wilaya == wilaya]

    def get_by_business(self, business_type: str) -> list:
        return [c for c in self.clients.values() if c.business_type == business_type]

    def get_by_status(self, status: str) -> list:
        return [c for c in self.clients.values() if c.status == status]

    def get_referral_network(self) -> dict:
        """Find clients in same wilaya who could refer each other."""
        wilaya_groups = {}
        for client in self.clients.values():
            if client.wilaya not in wilaya_groups:
                wilaya_groups[client.wilaya] = []
            wilaya_groups[client.wilaya].append(client)

        referrals = {}
        for wilaya, clients in wilaya_groups.items():
            if len(clients) > 1:
                referrals[wilaya] = [
                    {
                        "from": c.name,
                        "from_phone": c.phone,
                        "to": other.name,
                        "to_phone": other.phone,
                        "suggestion": f"Proposer à {other.name} ({other.business_type}) de recommander {c.name}",
                    }
                    for c in clients
                    for other in clients
                    if c.id != other.id
                ]
        return referrals

    def get_batch_summary(self) -> dict:
        """Summary stats for the dashboard."""
        total = len(self.clients)
        by_status = {}
        by_wilaya = {}
        by_business = {}
        total_value = 0

        for client in self.clients.values():
            by_status[client.status] = by_status.get(client.status, 0) + 1
            by_wilaya[client.wilaya] = by_wilaya.get(client.wilaya, 0) + 1
            by_business[client.business_type] = by_business.get(client.business_type, 0) + 1
            total_value += client.investment

        return {
            "total_clients": total,
            "by_status": by_status,
            "by_wilaya": by_wilaya,
            "by_business": by_business,
            "total_investment_value": total_value,
            "active_pipeline": by_status.get("new", 0) + by_status.get("quoted", 0) + by_status.get("in_progress", 0),
        }

    def generate_whatsapp_blast(self, wilaya: str, message: str) -> list:
        """Generate WhatsApp links for all clients in a wilaya."""
        clients = self.get_by_wilaya(wilaya)
        blasts = []
        for client in clients:
            blasts.append({
                "name": client.name,
                "phone": client.phone,
                "url": f"https://wa.me/{client.phone.replace('+','').replace(' ','')}",
                "message": message,
            })
        return blasts

    def save_dossier_draft(self, client_id: str, content: str, format: str = "md") -> str:
        """Save a dossier draft for a client."""
        if client_id not in self.clients:
            raise ValueError(f"Client {client_id} not found")

        filename = f"{client_id}_{datetime.now().strftime('%Y%m%d')}.{format}"
        filepath = DRAFTS_DIR / filename
        filepath.write_text(content, encoding="utf-8")

        self.clients[client_id].dossiers.append(filename)
        self.clients[client_id].last_updated = datetime.now().isoformat()
        self._save_clients()

        return str(filepath)

    def export_csv(self) -> str:
        """Export client list as CSV."""
        lines = ["ID,Name,Phone,Email,Wilaya,Business,Investment,Service,Status,Created,Referrals"]
        for c in self.clients.values():
            lines.append(
                f"{c.id},{c.name},{c.phone},{c.email},{c.wilaya},"
                f"{c.business_type},{c.investment},{c.service},{c.status},"
                f"{c.created_at},{c.referrals}"
            )
        csv_content = "\n".join(lines)
        csv_path = BATCH_DIR / f"clients_{datetime.now().strftime('%Y%m%d')}.csv"
        csv_path.write_text(csv_content, encoding="utf-8")
        return str(csv_path)


if __name__ == "__main__":
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    mgr = BatchManager()

    # Demo: add sample clients
    if not mgr.clients:
        sample_clients = [
            ("Ahmed Benali", "0555123456", "El Bayadh", "quincaillerie", 4600000),
            ("Fatima Bouchama", "0666789012", "El Bayadh", "boulangerie", 2500000),
            ("Mohamed Touati", "0777345678", "Oran", "restaurant", 8000000),
            ("Amina Hadj", "0555901234", "Oran", "cybercafe", 3500000),
            ("Youcef Mebarki", "0666567890", "Alger", "pharmacie", 7000000),
            ("Sara Khelifi", "0777234567", "Alger", "salon_coiffure", 2500000),
            ("Karim Zeroual", "0555890123", "Sétif", "garage", 5000000),
            ("Nadia Belkacem", "0666456789", "Sétif", "epicerie", 2000000),
        ]
        for name, phone, wilaya, biz, inv in sample_clients:
            mgr.add_client(name, phone, wilaya, biz, inv)

    summary = mgr.get_batch_summary()
    print(f"\n=== Batch Summary === {summary['total_clients']} clients")
    print(f"Pipeline actif: {summary['active_pipeline']}")
    print(f"Valeur totale: {summary['total_investment_value']:,} DZD")
    print(f"\nPar statut: {summary['by_status']}")
    print(f"Par wilaya: {summary['by_wilaya']}")
    print(f"Par activite: {summary['by_business']}")

    referrals = mgr.get_referral_network()
    for wilaya, refs in referrals.items():
        print(f"\n=== Referrals {wilaya} ===")
        for ref in refs:
            print(f"  -> {ref['suggestion']}")

    csv_path = mgr.export_csv()
    print(f"\nCSV exported: {csv_path}")
