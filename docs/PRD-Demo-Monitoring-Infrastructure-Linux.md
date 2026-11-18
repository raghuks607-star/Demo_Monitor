# Product Requirements Document (PRD)
## Demo Monitoring Infrastructure — Linux Servers

| Field | Value |
|---|---|
| **Document status** | Draft v0.1 |
| **Owner** | SRE / Platform Operations |
| **Audience** | Engineering, SRE L3, Platform, Demo stakeholders |
| **Last updated** | 2026-11-17 |
| **Scope** | Linux server monitoring (demo environment) |

---

## 1. Executive summary

Build a **self-contained demo monitoring stack** that observes Linux servers end-to-end: host metrics, service health, logs (light touch), dashboards, and alert routing. The goal is a repeatable, portable demo that shows how operations teams detect, diagnose, and respond to Linux infrastructure issues—not a production multi-region observability platform.

**Success looks like:** a facilitator can stand up the stack, point it at a small set of Linux hosts, walk through “healthy → degraded → recovered,” and leave stakeholders with a clear picture of monitoring value for Unix/Linux operations.

---

## 2. Problem statement

Stakeholders need a credible, hands-on demonstration of Linux server monitoring without depending on production tooling, customer data, or long provisioning cycles. Today there is no standardized demo that:

- Shows host-level signals (CPU, memory, disk, network, load)
- Surfaces process/service failure in a realistic way
- Ties metrics to alerts and operator-facing dashboards
- Can be reset and re-run consistently for training or executive demos

Without this, demos are ad hoc, brittle, or overfitted to a single vendor console.

---

## 3. Goals and non-goals

### 3.1 Goals

| ID | Goal |
|---|---|
| G1 | Monitor a small fleet of Linux demo hosts (target: 3–10 VMs/containers) |
| G2 | Collect core host metrics via agents/exporters with ≤ 30s scrape/collection interval (configurable) |
| G3 | Provide operator dashboards for fleet overview and single-host deep dive |
| G4 | Demonstrate alert lifecycle: fire → notify → acknowledge/silence → resolve |
| G5 | Support a scripted “failure injection” path for live demos (e.g., CPU burn, disk fill, stop service) |
| G6 | Document standup, teardown, and demo script so any SRE can run it |
| G7 | Prefer open-source, container-friendly components for portability |

### 3.2 Non-goals

| ID | Non-goal |
|---|---|
| NG1 | Production HA, multi-AZ, or multi-region design |
| NG2 | Full APM / distributed tracing / business KPI monitoring |
| NG3 | Windows or network-device monitoring (may be a later PRD) |
| NG4 | Long-term metrics retention beyond demo needs (default ≤ 7–15 days) |
| NG5 | Compliance attestations (SOC2 evidence packs, etc.) for the demo itself |
| NG6 | Auto-remediation / self-healing beyond optional demo hooks |

---

## 4. Users and personas

| Persona | Needs |
|---|---|
| **Demo facilitator (SRE L3)** | Reliable standup, clear demo script, failure injection knobs |
| **Operations engineer** | Familiar signals and workflows (host health, alerts, runbook cues) |
| **Engineering / platform lead** | Credible architecture story; clear path from demo → production pattern |
| **Executive / stakeholder** | “What do we see when something breaks?” in under 15 minutes |

---

## 5. Demo scenarios (must support)

1. **Fleet healthy** — All hosts green; baseline dashboards populate within minutes of standup.
2. **CPU / memory pressure** — Inject load on one host; dashboard and alert reflect stress within one scrape window (+ alert evaluation delay).
3. **Disk pressure** — Fill a demo volume/path; disk alerts fire; cleanup restores green.
4. **Service down** — Stop a monitored systemd service (or container); availability alert fires; restart clears it.
5. **Host unreachable** — Stop agent or block scrape briefly; “up” / target-down alert fires.
6. **Alert routing** — Show notification to a demo channel (Slack/webhook/email sink) and silence/ack behavior if the chosen stack supports it.

Each scenario must have: trigger method, expected signal, dashboard panel(s), alert name, and recovery steps.

---

## 6. Functional requirements

### 6.1 Metric collection (Linux hosts)

| ID | Requirement | Priority |
|---|---|---|
| FR-M1 | Collect CPU (usage, load, steal if available), memory (used/available/buffers/cache), disk (space, inode, IO), network (bytes/errors), filesystem mount health | P0 |
| FR-M2 | Collect process/service presence for a defined allowlist of demo services | P0 |
| FR-M3 | Expose host identity labels: `hostname`, `environment=demo`, `role`, `instance_id` | P0 |
| FR-M4 | Support Linux targets: RHEL/Rocky/Alma **or** Ubuntu (document supported distros) | P0 |
| FR-M5 | Optional: systemd unit state exporter or equivalent for service health | P1 |
| FR-M6 | Optional: light log shipping for journald/syslog of demo services (search + correlate, not full SIEM) | P2 |

### 6.2 Storage and query

| ID | Requirement | Priority |
|---|---|---|
| FR-S1 | Time-series store queryable by dashboards and alert rules | P0 |
| FR-S2 | Retention configurable; default suitable for demos (e.g., 7–15 days) | P0 |
| FR-S3 | Ability to reset/wipe series for a clean demo restart | P1 |

### 6.3 Visualization

| ID | Requirement | Priority |
|---|---|---|
| FR-D1 | **Fleet overview** dashboard: host count, unhealthy count, top CPU/mem/disk offenders | P0 |
| FR-D2 | **Host detail** dashboard: per-resource panels, linked from overview | P0 |
| FR-D3 | **Alerts** view: active firing / pending / resolved history for the demo window | P0 |
| FR-D4 | Dashboards versioned as code (JSON/YAML in repo) | P0 |
| FR-D5 | Dark/light readable for projector/screen share | P1 |

### 6.4 Alerting

| ID | Requirement | Priority |
|---|---|---|
| FR-A1 | Alert rules for: host down, high CPU, high memory, disk nearly full, service down | P0 |
| FR-A2 | Severity labels: `critical` / `warning` | P0 |
| FR-A3 | Route notifications to at least one demo sink (webhook and/or Slack and/or email) | P0 |
| FR-A4 | Support silence or inhibit during known demo setup windows | P1 |
| FR-A5 | Each alert references a short runbook URL or embedded “what to do” annotation | P1 |

### 6.5 Demo control plane

| ID | Requirement | Priority |
|---|---|---|
| FR-C1 | One-command or documented compose/k8s standup for the monitoring stack | P0 |
| FR-C2 | Failure-injection scripts/playbooks (CPU, disk, stop service, kill agent) | P0 |
| FR-C3 | Teardown / reset procedure that returns to clean baseline | P0 |
| FR-C4 | Seed config: scrape targets, alert rules, dashboards, notification sink | P0 |
| FR-C5 | Demo checklist (pre-flight, live script, debrief) | P1 |

### 6.6 Security (demo-appropriate)

| ID | Requirement | Priority |
|---|---|---|
| FR-SEC1 | No production credentials or customer data in the demo | P0 |
| FR-SEC2 | Default credentials documented and changeable; bind services to demo network only where practical | P0 |
| FR-SEC3 | Agents run least privilege feasible for host metrics | P1 |
| FR-SEC4 | TLS optional for demo; document when to enable for shared/lab networks | P2 |

---

## 7. Non-functional requirements

| ID | Requirement | Target |
|---|---|---|
| NFR1 | Standup time (stack + agents on prepared hosts) | ≤ 30 minutes for experienced facilitator |
| NFR2 | Metric freshness | Scrape/collection interval ≤ 30s |
| NFR3 | Alert detection latency (after condition true) | ≤ 2 minutes for P0 alerts (rule-dependent) |
| NFR4 | Host scale for demo | 3–10 Linux nodes comfortably |
| NFR5 | Portability | Runs on laptop lab, single VM, or small cloud VPC |
| NFR6 | Documentation | README + architecture diagram + demo script in repo |
| NFR7 | Idempotent config | Re-apply configs without manual UI clicking for core path |

---

## 8. Proposed architecture (reference)

> Stack choice is a **recommendation for the demo**, not a vendor mandate. Substitute equivalents if they preserve the requirements above.

```
                    ┌─────────────────────────────────────────┐
                    │           Demo observers                 │
                    │  (browser → Grafana / Alert UI)          │
                    └─────────────────┬───────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
         ▼                            ▼                            ▼
   ┌───────────┐              ┌──────────────┐             ┌──────────────┐
   │ Grafana   │◄────────────►│ Prometheus   │────────────►│ Alertmanager │
   │ dashboards│              │ (TSDB+rules) │             │ → webhook/   │
   └───────────┘              └───────▲──────┘             │   Slack sink │
                                      │                    └──────────────┘
                                      │ scrape
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
             ┌────────────┐   ┌────────────┐   ┌────────────┐
             │ Linux host │   │ Linux host │   │ Linux host │
             │ node_exp.  │   │ node_exp.  │   │ node_exp.  │
             │ (+ optional│   │            │   │            │
             │  process/  │   │            │   │            │
             │  systemd)  │   │            │   │            │
             └────────────┘   └────────────┘   └────────────┘
```

**Reference components**

| Layer | Reference choice | Role |
|---|---|---|
| Host metrics | Prometheus Node Exporter | Linux host telemetry |
| Service checks | systemd exporter / blackbox (optional) | Unit / endpoint health |
| TSDB + rules | Prometheus | Store, query, evaluate alerts |
| Alert routing | Alertmanager | Group, silence, notify |
| UI | Grafana | Dashboards |
| Packaging | Docker Compose (default) or small k8s | Fast standup |
| Injection | Bash/Ansible scripts | Controlled failures |

**Alternatives (acceptable if requirements met):** VictoriaMetrics, Mimir (overkill for demo), Zabbix, Netdata + centralization, commercial agents in “lab mode.” Document any substitution in the ADR.

---

## 9. Data model (minimum labels / signals)

**Required metric families (examples):**

- `node_cpu_seconds_total`, `node_load1`
- `node_memory_MemAvailable_bytes`, `node_memory_MemTotal_bytes`
- `node_filesystem_avail_bytes`, `node_filesystem_size_bytes`
- `node_network_receive_bytes_total` / `transmit`
- `up{job="node"}` (target health)

**Required labels:** `instance`, `job`, `hostname`, `env=demo`, `role`

**Alert examples (names illustrative):**

| Alert | Condition (illustrative) | Severity |
|---|---|---|
| `DemoHostDown` | `up == 0` for 1–2m | critical |
| `DemoHighCPU` | CPU util > 85% for 2m | warning |
| `DemoHighMemory` | Mem available < 10% for 2m | warning |
| `DemoDiskAlmostFull` | Filesystem > 85% for 2m | warning/critical by mount |
| `DemoServiceDown` | Expected unit inactive | critical |

Exact thresholds live in versioned rule files and are tuned for the injection scripts.

---

## 10. User experience / demo script outline

**Duration:** ~15–20 minutes live

1. **Pre-flight (T-10):** Stack healthy; targets up; notification sink connected.
2. **Baseline (2 min):** Show fleet overview — all green.
3. **Inject CPU (3 min):** Run burn script → dashboard spike → warning alert → explain threshold.
4. **Inject disk or service stop (4 min):** Show critical path and runbook annotation.
5. **Recovery (3 min):** Stop injection / restart service → alerts resolve → green restored.
6. **Debrief (3 min):** What maps to production (SLOs, on-call, retention, HA) vs what is demo-scoped.

---

## 11. Delivery plan (phased)

### Phase 0 — Spec & skeleton (this document)
- Agree stack, host count, distro, notification sink
- Repo layout and ADR for stack choice

### Phase 1 — MVP (P0)
- Compose stack: Prometheus, Alertmanager, Grafana
- Node Exporter on ≥ 3 Linux hosts (or compose sidecars for “fake fleet”)
- Fleet + host dashboards
- P0 alert rules + webhook sink
- Injection scripts + README + demo checklist

### Phase 2 — Demo polish (P1)
- Silences, runbook links, systemd/service monitoring
- Reset/wipe automation
- Projector-friendly dashboard pass
- Recorded walkthrough (optional)

### Phase 3 — Extensions (P2)
- Light log correlation
- Optional Windows follow-on PRD
- “Path to production” architecture appendix

---

## 12. Acceptance criteria

The demo is **accepted** when:

1. A new facilitator follows the README and brings the stack up without undocumented steps.
2. All P0 dashboards show live data from ≥ 3 Linux targets within 5 minutes of healthy standup.
3. Each of the six demo scenarios in §5 can be executed with expected alerts and recovery.
4. Alert notifications appear in the configured sink during a live run.
5. Teardown leaves no dependency on production systems; secrets used are demo-only.
6. Architecture and limitations are stated clearly for stakeholder Q&A.

---

## 13. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Demo flake (timing, scrape delay) | Tune intervals; wait cues in script; prefer longer `for:` on noisy alerts |
| Resource contention on laptop lab | Document minimum RAM/CPU; offer cloud-VM profile |
| Scope creep into production design | Enforce non-goals; keep “path to prod” as appendix only |
| Credential leakage into repo | Sample `.env.example`; gitignore secrets; pre-demo secret scan |
| Distro drift (RHEL vs Ubuntu paths) | Pin supported images; abstract injection scripts |

---

## 14. Open decisions (to resolve before Phase 1 build)

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | Packaging | Docker Compose vs mini-k8s | **Compose** for fastest demo |
| D2 | Real VMs vs containerized “hosts” | VMs / LXD / containers with node_exporter | **Containers OK for MVP**; 1–2 real VMs for credibility if available |
| D3 | Notification sink | Slack webhook / email / generic webhook UI | **Slack or webhook catcher** |
| D4 | Distro support | Ubuntu 22.04+ and/or Rocky 9 | Pick **one primary** for MVP |
| D5 | Logs in MVP? | Yes light / No | **No** for MVP (P2) |
| D6 | Auth on Grafana | Anonymous viewer vs basic auth | **Basic auth** with demo user |

---

## 15. Repository layout (proposed)

```
Cursor_Monitoring/
├── docs/
│   ├── PRD-Demo-Monitoring-Infrastructure-Linux.md  # this file
│   ├── architecture.md
│   ├── demo-script.md
│   └── adr/
│       └── 0001-stack-choice.md
├── docker-compose.yml
├── prometheus/
│   ├── prometheus.yml
│   └── rules/
├── alertmanager/
│   └── alertmanager.yml
├── grafana/
│   └── provisioning/...
├── agents/                    # node_exporter install notes / unit files
├── scripts/
│   ├── inject-cpu.sh
│   ├── inject-disk.sh
│   ├── stop-service.sh
│   └── reset-demo.sh
└── README.md
```

---

## 16. Success metrics (for the demo program)

| Metric | Target |
|---|---|
| Facilitator time-to-ready | ≤ 30 minutes |
| Live demo completion rate | ≥ 90% without severity-1 flake |
| Stakeholder comprehension check | Post-demo: can name 3 signals + alert path |
| Reuse | Same stack reused for internal SRE training within one quarter |

---

## 17. Appendix A — Glossary

| Term | Meaning |
|---|---|
| Exporter | Process that exposes metrics in Prometheus format |
| Scrape | Pull-based collection of metrics over HTTP |
| Silence | Temporary suppression of alert notifications |
| Injection | Controlled fault used only in demo/lab |

## 18. Appendix B — Out-of-scope production concerns (explicit)

Production would additionally require: HA Prometheus/Thanos or managed TSDB, authenticated remote write, SSO, secrets management, capacity planning, on-call schedules, SLO burn alerts, change management, and multi-tenant isolation. Those are intentionally excluded from this demo PRD.

---

## Document history

| Version | Date | Author | Notes |
|---|---|---|---|
| 0.1 | 2026-11-17 | Draft | Initial PRD for Linux demo monitoring |
