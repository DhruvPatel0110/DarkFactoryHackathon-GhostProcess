import asyncio
import os
import sys
import time
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure Windows UTF-8 stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from agents.config import MAX_REJECTION_CYCLES, BAND_ROOM_NAME, BAND_ROOM_ID
from agents.architect import ArchitectAgent
from agents.coder import CoderAgent
from agents.ghost_auditor import GhostAuditorAgent
from agents.gatekeeper import GatekeeperAgent

async def launch_dark_factory(task_prompt: str):
    start_time = time.monotonic()
    
    print("\n" + "=" * 75)
    print("      ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗██████╗ ██████╗  ██████╗ ")
    print("     ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝ ")
    print("     ██║  ███╗███████║██║   ██║███████╗   ██║   ██████╔╝██████╔╝██║      ")
    print("     ██║   ██║██╔══██║██║   ██║╚════██║   ██║   ██╔═══╝ ██╔══██╗██║      ")
    print("     ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   ██║     ██║  ██║╚██████╗ ")
    print("      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ")
    print("           AUTONOMOUS 4-SEAT DARK FACTORY Floor Orchestrator             ")
    print("=" * 75)
    print(f"Room Binding: {BAND_ROOM_NAME} ({BAND_ROOM_ID})")
    print(f"Human Dispatch: \"{task_prompt}\"\n")

    # 1. Seat 1: Architect
    architect = ArchitectAgent()
    arch_res = await architect.generate_blueprint(task_prompt)
    if arch_res.get("status") != "COMPLETED":
        print("[ERROR] Architect failed to produce blueprint. Aborting factory run.")
        return

    # 2. Execution & Quality Gate Feedback Loop (Max 3 Cycles)
    cycle = 1
    coder = CoderAgent()
    auditor = GhostAuditorAgent()
    gatekeeper = GatekeeperAgent()

    while cycle <= MAX_REJECTION_CYCLES:
        print(f"\n--- [FACTORY PIPELINE: CYCLE {cycle}/{MAX_REJECTION_CYCLES}] ---")

        # Seat 2: Coder
        coder_res = await coder.implement_codebase()
        if coder_res.get("status") != "SUCCESS":
            print("[WARN] Coder tests reported failures. Passing to Red Team for deeper inspection...")

        # Seat 3: Ghost Auditor (Blind Red Team)
        audit_res = await auditor.execute_audit()

        # Seat 4: Gatekeeper (Quality Arbiter)
        decision = await gatekeeper.evaluate_release(cycle=cycle)

        if decision.get("verdict") == "APPROVED":
            total_duration = time.monotonic() - start_time
            print("\n" + "=" * 75)
            print(f"🎉 FACTORY RUN COMPLETE: Production release sealed in {total_duration:.1f}s!")
            print(f"   - Design Spec    : {PROJECT_ROOT / 'DESIGN.md'}")
            print(f"   - Handoff Report : {PROJECT_ROOT / 'HANDOFF.md'}")
            print(f"   - Audit Report   : {PROJECT_ROOT / 'AUDIT_REPORT.md'}")
            print(f"   - Release Notice : {PROJECT_ROOT / 'RELEASE.md'}")
            print("=" * 75)
            return

        print(f"[REJECTION] Cycle {cycle} rejected. Remediation directives assigned to @Coder.")
        cycle += 1

    print(f"\n[ALERT] Reached maximum allowed revision cycles ({MAX_REJECTION_CYCLES}). Escalate to human review.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = (
            "Construct the complete Stage 1 Pocketful payments and double-entry ledger backend. "
            "Strict double-entry, zero-sum conservation, exact decimal strings, idempotency replay, "
            "and clean container startup under --network none."
        )
    asyncio.run(launch_dark_factory(task))
