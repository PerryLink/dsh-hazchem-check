# dsh-hazchem-check — Hazardous chemical register and major hazard source identification check

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-hazchem-check` reads one hazardous-chemical register with its major-hazard-source identification record — the site header plus one row per substance — and checks that register's own completeness and arithmetic: that each substance carries a name and a hazard class, that the stored quantity parses as a number, that a threshold is recorded, that the “major hazard source” verdict agrees with how the stored quantity compares with the threshold the register itself states, that a stored substance records its safety data sheet number, that no CAS number is repeated, that the header declares the identification basis, and that no template placeholder survives in the name column.

## What it looks like

![Terminal demo of dsh-hazchem-check: real output over its HZ-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-hazchem-check/main/docs/assets/dsh-hazchem-check-demo.png)

Real output from this plugin over its own `HZ-002` test fixture — not a mock-up. The rule pack ships no invented quotations, so a finding names both the clause it applied and the fact that the clause text was not obtained.

## What it answers

| You ask | What it answers |
|---|---|
| The register says “no”, but the stored quantity is above the threshold written beside it — is that caught? | Yes. `HZ-003` compares the two numbers the register itself carries and reports the row when the verdict disagrees with them. It does not decide whether the unit really is a major hazard source. |
| A row has no threshold at all. Does the check say anything? | Yes. `HZ-004` requires the threshold column to be filled on every row. It checks that a value is present, not that it is the right value for that substance — a `0` passes. |
| The chemical name is filled in but the hazard class is blank. | `HZ-001` requires both on each row and reports the row missing either one. It does not judge whether the class is correct. |
| The quantity column reads `1,500 kg` — will that still be read? | Yes. `HZ-002` takes the numeric part; only a quantity it cannot parse is reported. Whether the figure is true, or taken at the design maximum, is not checked. |
| Which rows must carry a safety data sheet number? | `HZ-006`: every row that has a stored quantity. The rule checks that the number is filled in, not that the sheet is complete or belongs to that substance. |
| The same CAS number appears twice, in two warehouses. | `HZ-007` reports a repeated CAS number, because it defeats both de-duplication and the quantity total. One substance split across warehouses is a legitimate shape: distinguish it in the storage-location column, or disable the rule. With no CAS column the rule reports that it could not run instead of passing silently. |

## Standards it follows

| Document | Number | Cited by rules |
|---|---|---|
| 《危险化学品安全管理条例》 | 国务院令第591号（2002年1月26日国务院令第344号公布，2011年2月16日国务院第144次常务会议修订通过，自2011年12月1日起施行） | HZ-001, HZ-002, HZ-003, HZ-004, HZ-006, HZ-008 |
| 《危险化学品重大危险源辨识》 | GB 18218—2018（2018-11-19发布，2019-03-01实施；全部技术内容为强制性；代替GB 18218—2009） | HZ-002, HZ-003 |
| 《危险化学品重大危险源辨识》 | GB 18218—2018（本次未取得条文） | HZ-005 |
| 《危险化学品安全管理条例》 | 国务院令第591号（本次未取得条文） | HZ-007 |

**Boundary:** this plugin checks a **危险化学品台账与重大危险源辨识记录** for completeness and arithmetic — that
each chemical names itself and its hazard class, that the stored quantity parses, that a threshold is recorded,
that **the major-hazard-source verdict agrees with how the stored quantity compares to the threshold the register
states**, that a stored chemical records its safety data sheet number, that CAS numbers are not duplicated, that
the register declares its identification basis, and that no placeholder survives. It does **not** decide whether a
unit constitutes a major hazard source, whether it must be registered, whether a safety assessment is required, or
whether it is a major hidden danger.

> ### ⚠️ What the standard says, and the four errors this plugin cannot find
>
> **GB 18218—2018 was obtained and read verbatim** (see `rules/evidence/clause-verification-tables.md`):
> issued **2018-11-19, in force 2019-03-01**, with the foreword stating 「**本标准的全部技术内容为强制性的**」 —
> the whole standard is mandatory — and it **supersedes GB 18218—2009** (the 2000 and 2009 editions are both
> withdrawn, so citing them is simply wrong). The definitions of 临界量 (3.3), 单元 (3.2) and 重大危险源 (3.4),
> the determination rule 4.1.2, and **table 1's first 35 rows** are all quoted in that report.
>
> **Table 1 is complete only to row 35 and table 2 was not obtained**, so no threshold value is built in and none
> can be checked. `HZ-003` compares the stored quantity against the threshold **the register itself records** and
> checks that the verdict agrees. It therefore **cannot find four classes of error**, and its own note says so:
>
> 1. **A threshold taken from the wrong substance or hazard class** — 4.1.2 requires table 1 for listed
>    substances and table 2 otherwise.
> 2. **A multi-hazard substance not given its lowest threshold** — 4.1.2 b): 「若一种危险化学品具有多种危险性，
>    按其中最低的临界量确定」. Registers carry one figure, so rounding up misses a major hazard source.
> 3. **The multi-substance correction** — within one unit, `S = q₁/Q₁ + q₂/Q₂ + … + qₙ/Qₙ ≥ 1` also constitutes a
>    major hazard source. **This plugin does not perform that summation**, because identification works per
>    **production or storage unit** (3.2, 3.5, 3.6) while a register lists substances without unit grouping.
> 4. **The quantity basis** — 4.2.2 requires the quantity to be taken **at the design maximum**, while a register
>    may record stock on hand.
>
> ⚠️ **Stay inside the standard's scope.** Clause 1 excludes **off-site transport of hazardous chemicals**
> (rail, road, water, air, pipeline), nuclear and military facilities, mining (except processing and storage), and
> offshore oil and gas extraction. Using this plugin on a **transport** consignment is out of scope — that is
> governed by dangerous-goods transport rules, not by GB 18218.
>
> A finding therefore means only "**the two numbers you wrote do not agree with your own verdict**". The four
> items above need a unit-by-unit calculation under the standard, which is a safety-assessment and
> regulator-determination task. **Every `excerpt` still says "本次未取得" and every rule stays `warn` or `info`**,
> because what this plugin checks is a register's internal consistency, not whether a threshold value is correct.

## Compatibility

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a site's register use `ptc` |

## What it does

Registers the `hazchem_check` tool. It reads one chemical register — the site header plus one row per substance —
applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `HZ-001` | the name and hazard class are recorded | warn | principle |
| `HZ-002` | the stored quantity parses as a number | warn | principle |
| `HZ-003` | the verdict agrees with quantity and threshold | warn | principle |
| `HZ-004` | a threshold is recorded | warn | principle |
| `HZ-005` | the register declares its identification basis | warn | principle |
| `HZ-006` | a stored chemical records its SDS number | warn | principle |
| `HZ-007` | CAS numbers are not duplicated | warn | principle |
| `HZ-008` | the name column holds no unreplaced placeholder | warn | principle |

## Install

```sh
dsh plugin --profile <name> add dsh-hazchem-check
dsh --profile <name> --dump-config | grep 'dsh-hazchem-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/hazchem-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `HZ-003` `valueField` / `limitField` / `verdictField` / `overValues` / `atMostValues` / `tolerance` — the three
  columns and the two verdict vocabularies, defaulting to `[是, Y, yes, true, 构成, 重大危险源, √]` and
  `[否, N, no, false, 不构成, 未构成]`.
- `HZ-008` `terms` — the placeholders to look for.

## Material format

The tool accepts JSON or YAML:

```yaml
company: 某某化工有限公司
site: 某某厂区
assessmentAt: 2026-03-01
basis: GB 18218—2018 与 2025 年版危险化学品目录
rows:
  - { 序号: '1', 化学品名称: 甲醇, CAS号: 67-56-1, 危险性类别: 易燃液体,
      储存位置: 罐区 T-01, 最大储存量: '80', 计量单位: t, 临界量: '500',
      是否重大危险源: 否, 安全技术说明书编号: SDS-2026-0018, 保管人: 李工 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the register's own
column names are kept, so a finding names the column it read.

## Rule sources

Rule data lives in `rules/hazchem-check.yaml`. Its header explains that the plugin holds no threshold table and
performs no multi-substance correction, and each rule's `note` repeats the part that matters for that rule. The
load-time guard still requires a document, clause, excerpt and source per rule, and still forbids a
principle-derived check from being `error`.

## Troubleshooting

- **`HZ-003` passed a threshold I know is wrong.** It compares against the threshold the register states.
  Whether that value belongs to the right substance and hazard class is a substantive question it does not touch.
- **It did not flag a unit that should be a major hazard source.** It has no threshold table and does not perform
  GB 18218's multi-substance summation. Work the unit out under the standard yourself.
- **`HZ-004` passes a threshold of `0`.** The rule checks that the column is filled, not what it contains. Only a
  person comparing against the standard can judge the value.
- **`HZ-007` never runs.** The register records no CAS numbers. Without a unique identifier the rule reports that
  it could not run rather than checking the wrong column.
- **`HZ-007` fires on one substance in two warehouses.** That is a legitimate register shape — say so in the
  storage-location column and disable the rule if your register is organised that way.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-hazchem-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-hazchem-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and the
check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hazchem-check contributors.
