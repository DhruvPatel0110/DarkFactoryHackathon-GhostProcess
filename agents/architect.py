import asyncio
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure Windows UTF-8 stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from agents.config import BAND_ROOM_ID, BAND_ROOM_NAME
from agents.llm_client import llm_client

class ArchitectAgent:
    """
    Seat 1: Lead Systems & Software Architect
    - Reads PROJECT_CONTEXT.md & Agents_Context/architect.md
    - Produces DESIGN.md (airtight technical architecture) and WORK_ITEMS.md (sequenced tasks)
    - Signals handoff to @Coder
    """
    def __init__(self):
        self.name = "Architect"
        mandate_dir = PROJECT_ROOT / "mandates" if (PROJECT_ROOT / "mandates").exists() else PROJECT_ROOT / "Agents_Context"
        self.mandate_path = mandate_dir / "architect.md"
        self.context_path = PROJECT_ROOT / "PROJECT_CONTEXT.md"
        self.design_path = PROJECT_ROOT / "DESIGN.md"
        self.work_items_path = PROJECT_ROOT / "WORK_ITEMS.md"

    def load_files(self) -> tuple[str, str]:
        mandate = self.mandate_path.read_text(encoding="utf-8") if self.mandate_path.exists() else ""
        context = self.context_path.read_text(encoding="utf-8") if self.context_path.exists() else ""
        return mandate, context

    async def generate_blueprint(self, task_prompt: str) -> dict:
        print("\n" + "=" * 65)
        print(f"🏛️  [SEAT 1: {self.name.upper()}] Starting System Architecture Blueprint...")
        print("=" * 65)

        mandate, context = self.load_files()

        system_prompt = (
            f"You are the Lead Systems Architect in the GhostProcess Autonomous Dark Factory.\n"
            f"Your standing mandate is:\n{mandate}\n\n"
            f"You strictly enforce mathematical invariants, clean architecture, and deterministic precision.\n"
            f"Output comprehensive, production-ready markdown documents with zero placeholders."
        )

        is_calc = "calculator" in task_prompt.lower()
        if is_calc:
            task_details = (
                "1. Generate DESIGN.md detailing:\n"
                "   - REST API interface contracts (/add, /subtract, /multiply, /divide)\n"
                "   - Pydantic models for request and response\n"
                "   - Error handling: division by zero returning HTTP 400 Bad Request\n"
                "2. Generate WORK_ITEMS.md listing sequenced tasks (WI-01 to WI-03) for the Coder."
            )
        else:
            task_details = (
                "1. Generate DESIGN.md detailing:\n"
                "   - Component topology & layer separation\n"
                "   - Strict double-entry ledger invariants & mathematical conservation\n"
                "   - SQLite tables, constraints, WAL mode, busy_timeout, and BEGIN IMMEDIATE write-locking\n"
                "   - REST API interface contracts (health, wallets, transfers, state reset/import/export)\n"
                "   - Exact decimal string parsing (reject >2 decimals, normalize <2 decimals)\n"
                "   - Idempotency deduplication mechanism\n"
                "2. Generate WORK_ITEMS.md listing sequenced, dependency-ordered tasks (WI-01 to WI-06) for the Coder."
            )

        prompt = (
            f"Human Dispatch Task: {task_prompt}\n\n"
            f"Project Context & Requirements:\n{context}\n\n"
            f"TASK:\n{task_details}\n\n"
            f"Format your response with explicit delimiters:\n"
            f"---BEGIN DESIGN.MD---\n[Content]\n---END DESIGN.MD---\n\n"
            f"---BEGIN WORK_ITEMS.MD---\n[Content]\n---END WORK_ITEMS.MD---"
        )

        print(f"[{self.name}] Analyzing requirements & synthesizing design via LLM engine...")
        raw_output = await llm_client.generate(prompt=prompt, system_prompt=system_prompt, temperature=0.1)

        # Parse output delimiters
        design_content = ""
        work_items_content = ""

        if "---BEGIN DESIGN.MD---" in raw_output and "---END DESIGN.MD---" in raw_output:
            design_content = raw_output.split("---BEGIN DESIGN.MD---")[1].split("---END DESIGN.MD---")[0].strip()
        else:
            design_content = raw_output.split("---BEGIN WORK_ITEMS.MD---")[0].strip()

        # Clean any leading/trailing marker relics
        if design_content.startswith("---BEGIN DESIGN.MD---"):
            design_content = design_content[len("---BEGIN DESIGN.MD---"):].strip()
        if design_content.endswith("---END DESIGN.MD---"):
            design_content = design_content[:-len("---END DESIGN.MD---")].strip()

        if "---BEGIN WORK_ITEMS.MD---" in raw_output and "---END WORK_ITEMS.MD---" in raw_output:
            work_items_content = raw_output.split("---BEGIN WORK_ITEMS.MD---")[1].split("---END WORK_ITEMS.MD---")[0].strip()
        elif "---BEGIN WORK_ITEMS.MD---" in raw_output:
            work_items_content = raw_output.split("---BEGIN WORK_ITEMS.MD---")[1].strip()

        if not work_items_content or len(work_items_content.strip()) < 100:
            if is_calc:
                work_items_content = """# Sequenced Implementation Work Items

- [ ] **WI-01: Calculator REST API Endpoints**
  - **Module:** `stage-1/app/main.py`
  - **Criteria:** Implement `/add`, `/subtract`, `/multiply`, and `/divide` accepting `{ "a": float, "b": float }` returning `{ "result": float }`.

- [ ] **WI-02: Error Handling & Invariant Enforcement**
  - **Module:** `stage-1/app/main.py`
  - **Criteria:** Explicit HTTP 400 Bad Request on division by zero (`b == 0`).

- [ ] **WI-03: Developer Unit Test Suite**
  - **Module:** `stage-1/tests/test_calculator.py`
  - **Criteria:** Comprehensive unit tests for all arithmetic operations and zero-division error handling with 100% pytest pass rate.
"""
            else:
                work_items_content = """# Sequenced Implementation Work Items

- [ ] **WI-01: Foundation & Database Persistence Engine**
  - **Module:** `stage-1/app/config.py`, `stage-1/app/database.py`, `stage-1/app/models.py`
  - **Criteria:** Asynchronous SQLite engine with WAL mode, busy_timeout=5000, declarative models for Wallets, Transfers, JournalEntries, and IdempotencyRecords.

- [ ] **WI-02: Core Double-Entry Service & Invariant Enforcement**
  - **Module:** `stage-1/app/services/wallet_service.py`, `stage-1/app/services/transfer_service.py`, `stage-1/app/services/state_service.py`
  - **Criteria:** Atomic execution with BEGIN IMMEDIATE write-locking, zero-sum conservation verification, balance derivation from immutable entries, non-negative balance protection, and idempotency deduplication.

- [ ] **WI-03: Transport Layer & Validation Schemas**
  - **Module:** `stage-1/app/schemas.py`, `stage-1/app/routes/` (`health.py`, `wallets.py`, `transfers.py`, `state.py`), `stage-1/app/main.py`
  - **Criteria:** Pydantic v2 schemas enforcing string-encoded exact decimals (reject sub-cent >2 decimals and scientific notation, normalize single decimal), REST route handlers, clean JSON error formatting.

- [ ] **WI-04: Developer Test Suite & Quality Verification**
  - **Module:** `stage-1/tests/conftest.py`, `stage-1/tests/test_wallets.py`, `stage-1/tests/test_transfers.py`, `stage-1/tests/test_precision.py`
  - **Criteria:** 100% pytest pass rate covering entity lifecycles, balanced transfers, idempotency deduplication, and decimal quantization.
"""

        # Write artifacts to workspace
        self.design_path.write_text(design_content, encoding="utf-8")
        self.work_items_path.write_text(work_items_content, encoding="utf-8")

        print(f"[{self.name}] Generated: {self.design_path.name} ({len(design_content)} bytes)")
        print(f"[{self.name}] Generated: {self.work_items_path.name} ({len(work_items_content)} bytes)")
        print(f"[{self.name}] Handoff ready -> Tagging @Coder")

        return {
            "design_path": str(self.design_path),
            "work_items_path": str(self.work_items_path),
            "status": "COMPLETED",
        }

async def main():
    agent = ArchitectAgent()
    task = "Build Pocketful clean-room payments and double-entry ledger backend with strict idempotency and zero-sum conservation."
    await agent.generate_blueprint(task)

if __name__ == "__main__":
    asyncio.run(main())
