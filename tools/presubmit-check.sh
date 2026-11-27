#!/usr/bin/env bash
# Pre-submission checks for Kiroween 2026. Run from the repo root: bash tools/presubmit-check.sh
# Exits non-zero if any required check fails. Warnings do not fail the run.
set -uo pipefail
fail=0; warn=0
ok()   { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; fail=$((fail+1)); }
note() { printf '  \033[33mWARN\033[0m %s\n' "$1"; warn=$((warn+1)); }

echo "== Kiro evidence"
if [ -d .kiro ]; then ok ".kiro exists at repo root"; else bad ".kiro missing at repo root (required by the rules)"; fi
for d in steering specs hooks; do
  if [ -d ".kiro/$d" ] && [ -n "$(ls -A ".kiro/$d" 2>/dev/null)" ]; then ok ".kiro/$d has content"; else bad ".kiro/$d missing or empty"; fi
done
if [ -d .kiro ] && git check-ignore -q .kiro 2>/dev/null; then bad ".kiro is gitignored (can disqualify the submission)"; else ok ".kiro is not gitignored"; fi
if [ -d .kiro ] && [ -z "$(git ls-files .kiro | head -1)" ]; then bad ".kiro exists but nothing in it is committed"; fi

echo "== Licence and docs"
if [ -f LICENSE ] || [ -f LICENSE.md ]; then ok "licence file present"; else bad "no LICENSE file (must be visible in the repo About box)"; fi
if grep -qi "kiro" README.md 2>/dev/null; then ok "README mentions Kiro"; else bad "README does not mention Kiro"; fi
if [ "$(wc -l < README.md 2>/dev/null || echo 0)" -ge 15 ]; then ok "README has real content"; else bad "README is nearly empty (fails the 30-second test)"; fi

echo "== Skeleton Crew structure"
for a in apps/lazarus apps/chimera; do
  if [ -d "$a" ]; then ok "$a present"; else bad "$a missing (Skeleton Crew needs two app folders)"; fi
done

echo "== Secrets"
if git check-ignore -q .env 2>/dev/null; then ok ".env is gitignored"; else bad ".env is not gitignored"; fi
if [ -n "$(git ls-files | grep -E '(^|/)\.env($|\.)' | grep -v '\.env\.example$')" ]; then bad "a .env file is tracked by git"; else ok "no .env file tracked"; fi
PAT='AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|xox[abpr]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|KIRO_API_KEY=[^[:space:]$"'"'"'{]+'
if git grep -nIE "$PAT" -- . ':!tools/presubmit-check.sh' >/tmp/ns-secrets.txt 2>/dev/null; then bad "possible secrets in tracked files:"; sed 's/^/        /' /tmp/ns-secrets.txt | head -20; else ok "no secret patterns in tracked files"; fi
if git log -p --all -- . ':!tools/presubmit-check.sh' 2>/dev/null | grep -nE "^\+.*($PAT)" >/tmp/ns-hist.txt; then bad "possible secrets in git history (rotate the key, then rewrite history):"; head -10 /tmp/ns-hist.txt | sed 's/^/        /'; else ok "no secret patterns in git history"; fi

echo "== Submission reminders"
note "Video: under 3 minutes, public on YouTube, shows a spec, a hook or steering on screen"
note "Devpost: Kiro named in the description and in 'Built With'; Skeleton Crew category selected"
note "Kiro Crew bonus: separate public repo created during the submission period, same GitHub account"

echo
if [ "$fail" -eq 0 ]; then echo "All required checks passed ($warn reminders)."; else echo "$fail required check(s) failed, $warn reminders."; fi
exit "$fail"
