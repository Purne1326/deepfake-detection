# 🛡️ Deepfake Detection System - Evaluation Guide

This document outlines the key features to showcase during the project evaluation.

## 1. System Architecture Overview
*   **Member 2**: Platform Integration & Scraping.
*   **Member 3**: AI Detection Engines (Deepfake & NudeNet).
*   **Member 4**: Compliance, Takedown Logic & Audit Logging.
*   **Member 5**: Command & Control Dashboard (Oversight).

## 2. The Command Dashboard (Port 5000)
*   **Detection Trends**: Show the SVG graph (real-time data from `audit.db`).
*   **Threat Level**: Explain how it shifts from `NORMAL` to `CRITICAL` based on the highest risk score in the pending queue.
*   **Account Switcher**: (Bottom left) Click the ⚙️ icon to switch between *Admin*, *Forensic*, and *Compliance* views.

## 3. Automated Mitigation Flow
1.  Open the **Dummy Social Platform** (Port 5001).
2.  Observe the "Verified Human" vs "Identity Protected" badges.
3.  The **Orchestrator** (background process) periodically scrapes new posts.
4.  When a deepfake is detected (e.g., `bad_actor_99` posting about `Ananya`), the system sends a Takedown Request.
5.  **Refresh the Social Feed**: The post content is replaced by a "IDENTITY THREAT NEUTRALIZED" forensic banner.

## 4. Manual Forensic Scan
1.  Navigate to **Forensic Scan** on the Sidebar.
2.  Upload any image (e.g., from `demo_assets`).
3.  Show the AI returning **Deepfake Probability** and **Nudity Status**.
4.  Explain that this event is immediately logged to the **Audit Trail** for legal compliance.

## 5. Audit & Reporting
*   **Audit Trail**: Show the immutable record of every system action.
*   **Reporting**: Demonstrate the "Quarterly Forensic Audit" text export.

---
*Good luck with your evaluation!*
