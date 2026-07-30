# claude-skills — the `app-factory` marketplace

Reusable [Claude Code](https://claude.com/claude-code) skills extracted from
[OrthoZ](https://github.com/dylanPerinetti/OrthoZ)'s proven patterns, packaged
as a plugin marketplace. Goal: build the next applications — each with **its
own** setup, profile, branding and design — without re-deciding what OrthoZ
already settled, and ship them to the VPS with the same safety net.

## Install (in any project)

```
/plugin marketplace add <owner>/claude-skills
/plugin install app-foundation@app-factory
/plugin install app-modules@app-factory
/plugin install app-delivery@app-factory
```

Skills then trigger automatically when a task matches their description, or
explicitly: `/app-delivery:vps-deploy-pipeline`, `/app-foundation:laravel-app-bootstrap`, …
After updating this repo: `/plugin marketplace update app-factory`.

## The three plugins

### `app-foundation` — start a new app

| Skill | What it installs |
|---|---|
| `laravel-app-bootstrap` | Production-grade skeleton: Services/Data/Enums/Contracts layout, Pest + blocking coverage, Pint, PHPStan/Larastan, Rector, Vite, clean `.env.example` |
| `auth-rbac-permissions` | Named accounts, roles, atomic `Permission` enum (zero hardcoded role checks), Gates, throttle, user admin with anti-lockout |
| `user-profile-module` | Avatar editor, audited password change with current-password proof, theme & preferences |
| `app-settings-branding` | DB-driven `SettingsService` (cache + encrypted values), branding panel (name, palette, logos → favicons/PWA icons), write-only credential connectors with test button |
| `blade-design-system` | Hand-rolled CSS design system, Blade component kit, light/dark themes, FR/EN i18n |

### `app-modules` — feature modules, à la carte

| Skill | What it installs |
|---|---|
| `audit-gdpr-toolkit` | AuditLogger + viewer, retention purges, per-person JSON export, idempotent anonymization |
| `pwa-offline-shell` | Settings-driven manifest, service worker, offline page, lossless offline action queue |
| `scan-input-module` | Camera QR/barcode + scanner gun + manual entry, debounce, unknown-code binding |
| `crud-resource-module` | The resource recipe: list/search/sort, detail, gated edits, audited writes, CSV export, soft-archive |
| `email-sequence-nurturing` | Editable bilingual template library, scheduled D+N sender, signed unsubscribe, self-test sends |
| `ai-assistant-integration` | Multi-provider AI behind one contract, write-only encrypted keys, allow-listed read-only tools, quotas & retention |
| `admin-observability-suite` | KPI dashboard, bounded error-log reader, guarded DB admin tool |
| `readonly-sync-connector` | Read-only mirror of an external system of record, sync journal, degraded mode |
| `onboarding-whats-new` | First-login guided tour + once-per-release notes modal, per-user tracking |
| `feedback-roadmap-module` | In-app ideas/votes/comments, gated arbitration, optional GitHub deployments board |

### `app-delivery` — CI + VPS

| Skill | What it installs |
|---|---|
| `ci-quality-gates` | Blocking CI: Pint, PHPStan, coverage gate, security audits, MySQL migrations checks, front build, E2E, one aggregated required check |
| `vps-provision` | One more app on the VPS: PHP-FPM, Nginx vhost, MariaDB, deploy user + minimal sudoers, scheduler cron, systemd queue worker, HTTPS, off-server backups |
| `vps-deploy-pipeline` | Deploy **any GitHub repo** to the VPS: deploy.sh (DB backup, health check, auto-rollback), rollback.sh, deploy.yml with **continuous / scheduled / manual** triggers |

## Typical flows

- **New app, zero to deployed**: `laravel-app-bootstrap` → `auth-rbac-permissions` → `app-settings-branding` → `blade-design-system` → `user-profile-module` → `ci-quality-gates` → `vps-provision` → `vps-deploy-pipeline`. Add `app-modules` skills as features demand.
- **Existing repo, just add deployment**: `ci-quality-gates` → `vps-provision` → `vps-deploy-pipeline` (pick continuous, scheduled or manual triggering per repo).

## Design principles

See [`CONVENTIONS.md`](CONVENTIONS.md). In short: skills are **parameterized,
never OrthoZ-specific** (`{{APP_NAME}}`, `{{APP_SLUG}}`, …); template files end
in `.stub`; **no secrets ever** in templates or skills; OrthoZ is cited as the
reference implementation but every skill is self-sufficient without it.
