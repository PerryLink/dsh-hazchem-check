# Changelog

## 0.2.2

- Correct the document named by HZ-002, HZ-003 and HZ-004. All three carried the
  right decree number (国务院令第591号), the right article numbers (第十九条,
  第二十五条) and verbatim text whose own wording says 「本条例所称」, but the
  `document` field named 《危险化学品重大危险源辨识》 - a national standard that
  does not contain those articles. The rendered report therefore told a reader
  that a GB standard says something it does not say. The evidence record has
  always attributed both passages to 《危险化学品安全管理条例》, so only the
  pointer was wrong, not the quotation.

  The citation gate could not have caught this: it checks that each excerpt is
  traceable in `rules/evidence/`, and every excerpt was. It did not check that
  the excerpt's document and number belong to the same instrument. A scan of all
  408 rules across the 53 checkers found no other rule with this mismatch.

## 0.2.1

- Ship `CHANGELOG.md` and `SECURITY.md` inside the package. `files` is an
  allowlist and neither was on it, so no release note had ever reached anyone
  who installed this package, and npm had no changelog section to show.
## 0.2.0

- Release infrastructure brought to the family standard: `verify:self-contained`,
  `check:lockfile`, `check:readmes` and `check:citations` gates, a `prepublishOnly` that
  re-runs the whole chain, SECURITY.md, dependabot, and the OpenSSF Scorecard workflow.
- `check:citations` enforces the rule this pack's own header states: every `excerpt`
  must be a verbatim quotation, findable in `rules/evidence/`. Rules that are not
  traceable yet are listed in `rules/citations-baseline.json`, and that file can only
  shrink - anything new has to be sourced before it can land.
- The README install command now names the published package instead of a local tarball.
- Five-language READMEs hold the same section count and the same configuration keys.
- Rule pack: 8 rules across HZ-001..HZ-008.
- Licensed Apache-2.0.
