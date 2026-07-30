# Conventions for skills in this marketplace

These rules keep the 18 skills coherent and safe to apply to any project.

## Parameterization — never cloned

Skills must not assume OrthoZ: no orthodontics, no Orthokis, no fixed palette,
paths or hostnames. Anything project-specific is a placeholder the skill asks
for before writing files:

| Placeholder | Meaning | Example |
|---|---|---|
| `{{APP_NAME}}` | Display name | `MediStock` |
| `{{APP_SLUG}}` | kebab/snake identifier: repo, DB, `/var/www/<slug>`, service names | `medistock` |
| `{{PHP_VERSION}}` | PHP series | `8.4` |
| `{{NODE_VERSION}}` | Node LTS | `20` |
| `{{COVERAGE_MIN}}` | Blocking coverage % | `90` |
| `{{RUNNER_LABELS}}` | GitHub Actions `runs-on` value | `[self-hosted, vps]` or `ubuntu-latest` |
| `{{DOMAIN}}` / `{{DOMAIN_OR_IP}}` | Public host | `app.example.fr` |

## Templates are `.stub` files

Copy → strip the `.stub` suffix → replace every `{{…}}` token → verify no
token remains (`grep -rn '{{' <destination>`). The suffix keeps linters,
static analysis and YAML parsers away from files that are intentionally not
yet valid.

Template comments are in **French** (they come from OrthoZ and serve the same
team); SKILL.md files are in **English** (they are prompts for Claude —
generated UI copy still follows the target app's language).

## No secrets, anywhere, ever

No IPs, hostnames, keys, tokens or passwords in skills or templates. Secrets
live in GitHub Actions secrets and server-side `.env` files. Before committing
a new/updated skill: `grep -rniE '(BEGIN (RSA|OPENSSH)|api[_-]?key|token|passwo?rd)=?:? *[A-Za-z0-9]' <skill-dir>` plus a manual look at anything host-like.

## Anatomy of a skill here

```
skills/<name>/
├── SKILL.md          # frontmatter: name + trigger-rich description; lean imperative body
└── templates/        # optional .stub files, ready to instantiate
```

- Description = the triggering mechanism: say what it does AND when to use it.
- Body under ~120 lines: parameters to collect, method with the *why* behind
  non-obvious steps, verification checklist, reference-implementation pointers.
- Cite OrthoZ paths as the canonical example, but the skill must be fully
  usable in a session that has no access to OrthoZ.

## Versioning

Bump the plugin's `version` in its `.claude-plugin/plugin.json` (and the
marketplace entry) whenever its skills change behavior. Consumers refresh with
`/plugin marketplace update app-factory`.

## Definition of done for a new skill

1. Frontmatter description tested against realistic phrasings (would it trigger?).
2. Templates instantiate cleanly (no leftover `{{…}}`).
3. Verification checklist is executable — each item is a command or an observable fact.
4. No secret, no OrthoZ-specific value outside "Reference implementation" sections.
