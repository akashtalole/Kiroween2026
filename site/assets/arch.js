/* Clickable architecture diagram for Night Shift. Each node links to the lab or doc that explains it. */
(function () {
  "use strict";
  var NODES = [
    { id: "humans", x: 20, y: 200, t: "Humans", s: "intent, approvals, review", kind: "human", href: "lab.html?id=04-specs-ears-pbt", d: "People set intent and boundaries, answer the question queue, approve exceptions and review the morning briefing. Every touch is logged." },
    { id: "intake", x: 215, y: 70, t: "Intake + Spec Gate", s: "EARS, clarity check", href: "lab.html?id=03-hooks", d: "Turns an intent paragraph or issue into EARS requirements. Vague or untestable specs are parked in a question queue with a recommended default." },
    { id: "backlog", x: 215, y: 330, t: "Ranked backlog", s: "scoped tasks", href: "lab.html?id=06-mcp-servers", d: "A steady queue of well-scoped tasks, shared across IDE, CLI, Web and Crew through nightshift-mcp." },
    { id: "bots", x: 410, y: 30, t: "Crew bots", s: "health, docs, cost", href: "lab.html?id=07-crew-night-conductor", d: "Always-on Kiro Crew bots: pipeline health, docs sync, dependency hygiene, cost governor. Each has its own memory and limits." },
    { id: "conductor", x: 410, y: 200, t: "Night Conductor", s: "Crew job, parallel", href: "lab.html?id=07-crew-night-conductor", d: "A scheduled Crew job drains the backlog into parallel git worktrees, budget-capped, while the humans sleep." },
    { id: "briefing", x: 410, y: 395, t: "Morning briefing", s: "what needs you", href: "doc.html?doc=night-shift#10-human-touch-index-the-measurable-claim", d: "One page each morning: merged overnight, queued for you, open questions, spend, and the Human Touch Index." },
    { id: "workers", x: 605, y: 70, t: "Headless workers", s: "kiro-cli, worktrees", href: "lab.html?id=07-crew-night-conductor", d: "Role agents (builder, tester, reviewer, security, scribe) run non-interactively with scoped tool trust, each in its own worktree." },
    { id: "gate", x: 605, y: 330, t: "Correctness gate", s: "property tests, scans", href: "lab.html?id=05-policy-engine-pbt", d: "Property-based tests derived from requirements, unit tests, lint and security scans; failures feed back to the builder for up to three retries." },
    { id: "policy", x: 800, y: 200, t: "Policy engine", s: "deterministic tiers", kind: "policy", href: "lab.html?id=05-policy-engine-pbt", d: "Deterministic code, not an agent, decides merge or escalate. Risk can only rise, never fall, as signals are added; verified with property tests." },
    { id: "merge", x: 800, y: 50, t: "Auto-merge", s: "tiers A0, A1", href: "doc.html?doc=night-shift#6-autonomy-policy-how-minimal-human-intervention-stays-safe", d: "Low-risk changes with all gates green merge to a protected integration branch with an evidence pack attached." },
    { id: "queue", x: 800, y: 350, t: "Exception queue", s: "tiers A2, A3", href: "doc.html?doc=night-shift#7-evidence-pack-per-task", d: "Public API, dependency, auth, infra and migration changes wait for a human, with a two-minute evidence pack to decide from." }
  ];
  var EDGES = [["humans", "intake"], ["intake", "backlog"], ["backlog", "conductor"], ["bots", "conductor"], ["conductor", "workers"], ["workers", "gate"], ["gate", "policy"], ["policy", "merge"], ["policy", "queue"], ["queue", "briefing"], ["briefing", "humans"]];
  var W = 170, H = 66;
  var host = document.getElementById("arch"); if (!host) return;
  var byId = {}; NODES.forEach(function (n) { byId[n.id] = n; });
  function anchor(a, b) { // point on a's box edge toward b's centre
    var ax = a.x + W / 2, ay = a.y + H / 2, bx = b.x + W / 2, by = b.y + H / 2, dx = bx - ax, dy = by - ay;
    var sx = dx === 0 ? Infinity : (W / 2) / Math.abs(dx), sy = dy === 0 ? Infinity : (H / 2) / Math.abs(dy), s = Math.min(sx, sy);
    return [ax + dx * s, ay + dy * s];
  }
  var svg = '<svg viewBox="0 0 1000 480" role="img" aria-label="Night Shift architecture: humans, intake, backlog, conductor, workers, gate, policy engine, merge and exception queue"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z"/></marker></defs>';
  EDGES.forEach(function (e) { var a = byId[e[0]], b = byId[e[1]], p = anchor(a, b), q = anchor(b, a); svg += '<path class="edge" d="M' + p[0].toFixed(1) + " " + p[1].toFixed(1) + "L" + q[0].toFixed(1) + " " + q[1].toFixed(1) + '"/>'; });
  NODES.forEach(function (n) {
    svg += '<a href="' + n.href + '" class="node ' + (n.kind || "") + '" data-id="' + n.id + '" tabindex="0"><title>' + n.t + "</title><rect x=\"" + n.x + '" y="' + n.y + '" width="' + W + '" height="' + H + '"/><text x="' + (n.x + 14) + '" y="' + (n.y + 28) + '">' + n.t + '</text><text class="sub" x="' + (n.x + 14) + '" y="' + (n.y + 48) + '">' + n.s + "</text></a>";
  });
  svg += "</svg>";
  host.innerHTML = svg + '<div class="arch-preview" id="arch-preview" aria-live="polite"></div>';
  var prev = document.getElementById("arch-preview");
  function show(id) {
    var n = byId[id]; if (!n) return;
    Array.prototype.forEach.call(host.querySelectorAll(".node"), function (el) { el.classList.toggle("active", el.getAttribute("data-id") === id); });
    prev.innerHTML = "<h4>" + n.t + "</h4><p>" + n.d + '</p><a href="' + n.href + '">Open the lab or section →</a>';
  }
  Array.prototype.forEach.call(host.querySelectorAll(".node"), function (el) {
    ["mouseenter", "focus"].forEach(function (ev) { el.addEventListener(ev, function () { show(el.getAttribute("data-id")); }); });
  });
  show("policy");
})();
