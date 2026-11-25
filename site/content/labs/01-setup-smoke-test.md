# Lab 01 · Install and smoke-test Kiro CLI and Crew

**Goal:** prove the headless-worker design is viable before building anything else, then run the four-surface bake-off (experiment E1).

> Everything on this page comes from the Kiro docs read on 2026-11-25. If a command differs on your machine, trust `kiro-cli --help` and the docs.

## 1. Install the CLI

```bash
curl -fsSL https://cli.kiro.dev/install | bash
kiro-cli login
```

## 2. The day-one check

Headless mode runs a prompt with no one at the keyboard. `--no-interactive` takes the instruction as an argument or from stdin. Add `--v3` so the run does not depend on the default harness, and trust only the tools you need:

```bash
cd your-repo
kiro-cli chat --v3 --no-interactive --trust-tools=read_file,grep_search \
  "List the top-level files in this repository and say what each is for"
```

If this prints an answer, the whole overnight-worker design works. If you see `[denied] tool permission approval is not supported in non-interactive mode`, the tool you need is not trusted: add it to `--trust-tools`, or write a scoped `permissions.yaml` rule (preferred over `--trust-all-tools`).

**Authentication:** headless runs use either your stored login or a `KIRO_API_KEY` environment variable. A stored login takes precedence. API keys are documented for Pro, Pro+, Pro Max and Power plans. *Verify that your hackathon credits allow key generation; if not, the stored login is enough on your own machine.*

## 3. Install Kiro Crew

```bash
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh
kirocrew setup     # interactive: data dir, agent, credentials
kirocrew doctor    # verify everything is wired up
kirocrew gateway   # starts the server at http://localhost:5476
```

Open `http://localhost:5476`. The desktop app is an alternative that bundles the gateway.

## 4. Experiment E1: the four-surface bake-off

Give the **same small task** to the IDE, CLI, Web and Crew, each from a clean branch:

> Add a `--json` flag to the ledger export command, with requirements, tests and docs.

Record one entry per surface in `docs/kiro-log.md`:

```
## <date> E1: ledger --json on <surface>
Surface: IDE|CLI|Web|Crew     Agent: default
Metrics: time=<..> credits=<..> human_msgs=<..> prompts=<..> retries=<..> tests_first_pass=<y/n> diff_lines=<..>
Result: <one paragraph>
Evidence: <transcript or PR link>
Surprise: <what you did not expect>
```

## Checkpoint

- [ ] Headless prompt returns an answer
- [ ] `kirocrew doctor` is green
- [ ] Four E1 entries logged (or a note on why a surface was skipped, e.g. plan tier)
