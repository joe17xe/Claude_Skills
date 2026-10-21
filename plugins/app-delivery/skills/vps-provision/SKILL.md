---
name: vps-provision
description: Provision a VPS to host one more Laravel application alongside existing ones — PHP-FPM, Nginx vhost, MariaDB database, Node, a restricted deploy user with minimal sudoers, the Laravel scheduler cron, a systemd queue worker, HTTPS via certbot, off-server backups and health probes — without harming the apps already on the server. Use this whenever the user wants to put a new app on their server/VPS, set up hosting, add a site to an existing server, or prepare infrastructure before enabling automated deployment.
---

# VPS provisioning (one more app on the same server)

One VPS hosts several apps if each gets: its own directory, database, Nginx vhost, queue service, SSH alias and cron line — and shares the PHP/Node toolchain. Run these steps **once per application**, preferably through the shipped `provision.sh` (idempotent, safe to re-run). Never write secrets into the repo; everything secret lands in the server-side `.env` or GitHub secrets.

## Shared-server rules (non-negotiable)

Assume other apps already live on the server. Provisioning this one must never change what they depend on:

1. **No `artisan` before `composer install`.** `php artisan key:generate` on a fresh clone crashes (no `vendor/`) and leaves `.env` keyless and world-readable (664). Generate the key directly: `APP_KEY=base64:$(openssl rand -base64 32)` (only if `.env` has no `base64:` key yet), then `chown deploy:www-data .env && chmod 640 .env`.
2. **Never upgrade a shared package.** Install only the packages that are missing, with `apt-get install --no-upgrade`. Simulate first (`apt-get install -s --no-upgrade <missing…>`): any `Inst pkg [oldver] …` line means an installed package would be upgraded (e.g. a new `php8.4-intl` pulling `php8.4-common` 8.4.24 → 8.4.27 for every site) → abort unless `ALLOW_UPGRADE=1`. Same for Node: install if absent, never bump an existing older Node without `ALLOW_UPGRADE=1`.
3. **Never rewrite `~deploy/.ssh/config`.** Other repos' deploys use their own keys there. Append a per-app block only if absent — `Host github.com-{{APP_SLUG}}` / `HostName github.com` / `User git` / `IdentityFile ~/.ssh/{{APP_SLUG}}_repo` / `IdentitiesOnly yes` — clone via `git@github.com-{{APP_SLUG}}:{{GITHUB_REPO}}.git`, and `git remote set-url origin` on an existing clone. Add github.com to `known_hosts` only if `ssh-keygen -F github.com` finds nothing.
4. **Never remove another app's cron line.** The deploy crontab carries every app's scheduler. Append this app's line only when no line contains `cd /var/www/{{APP_SLUG}} && `; never filter out `schedule:run` lines.
5. **Per-app files only**: `/etc/sudoers.d/{{APP_SLUG}}-*` (validated with `visudo -cf` before install — a broken sudoers breaks sudo server-wide), `sites-available/{{APP_SLUG}}`, `{{APP_SLUG}}-queue.service`, `/root/.{{APP_SLUG}}_db_password`. Run `nginx -t` before every reload and disable only this vhost if it fails. Use `php{{PHP_VERSION}}` explicitly (also for Composer): the default `php` may be another site's version.

## Parameters

`{{APP_SLUG}}`, `{{APP_NAME}}`, `{{DOMAIN}}` / `{{DOMAIN_OR_IP}}`, `{{GITHUB_REPO}}` (owner/repo), `{{PHP_VERSION}}` (e.g. 8.4), `{{NODE_VERSION}}` (e.g. 22), DB engine (MariaDB default, SQLite for single-seat demos).

## Files to instantiate (strip `.stub`, replace `{{…}}`)

| Template | Destination in the app repo | Role |
|---|---|---|
| `provision.sh.stub` | `deploy/provision.sh` | the whole method below, shared-server safe |
| `env.production.stub` | `deploy/env.production.example` | `.env` skeleton (no secrets) copied by provision.sh |
| `nginx.conf.stub` | `deploy/nginx.conf` | vhost; provision.sh rewrites `server_name` with `DOMAIN` |
| `queue.service.stub` | `deploy/{{APP_SLUG}}-queue.service` | systemd queue worker |

Then on the VPS, as root: copy `deploy/provision.sh` over and `bash provision.sh` (`DOMAIN=… sudo -E bash provision.sh` for a preprod host). First run prints the Deploy Key and stops: add it (read-only) on GitHub, re-run.

## Method (what provision.sh does, as root)

1. **Shared toolchain** — only missing packages, `--no-upgrade`, simulation guard (rule 2): PHP-FPM {{PHP_VERSION}} + extensions (`mbstring xml curl zip intl gd sqlite3 mysql bcmath`), Nginx, MariaDB, git, certbot, Composer, Node LTS.
2. **Database** — `{{APP_SLUG}}` database + dedicated user bound to `127.0.0.1`, strong generated password kept in `/root/.{{APP_SLUG}}_db_password` and the server `.env` only.
3. **Deploy user** — `deploy` in `www-data`, sudoers limited to `systemctl reload php{{PHP_VERSION}}-fpm`; if a self-hosted runner user exists, it may run only this app's `deploy.sh`/`rollback.sh` as `deploy`.
4. **Deploy Key & SSH alias** — per-app key `~deploy/.ssh/{{APP_SLUG}}_repo`, appended `Host github.com-{{APP_SLUG}}` block, known_hosts if missing (rule 3).
5. **Code & env** — clone to `/var/www/{{APP_SLUG}}` via the alias, `.env` from `env.production.example` (DB password, `APP_URL`, `SESSION_SECURE_COOKIE` filled), key via openssl, `640 deploy:www-data` (rule 1). Production: `APP_ENV=production`, `APP_DEBUG=false`.
6. **First build** — `php{{PHP_VERSION}} composer install --no-dev --optimize-autoloader`, `npm ci && npm run build`, `migrate --force`, `storage:link`, `config:cache route:cache view:cache event:cache`; `storage` and `bootstrap/cache` group-writable for `www-data`. Create the first admin by hand afterwards.
7. **Nginx vhost** — root MUST point at `/public`; warns (never edits) if another enabled vhost already serves the domain; `nginx -t` then reload.
8. **HTTPS** — `certbot --nginx -d {{DOMAIN}} --redirect` when the host is a domain; then also set the repo's GitHub `APP_URL` variable to https.
9. **Scheduler cron & queue** — append-only cron line (rule 4) `* * * * * cd /var/www/{{APP_SLUG}} && php{{PHP_VERSION}} artisan schedule:run >> /dev/null 2>&1`; `{{APP_SLUG}}-queue` enabled. Deploys call `artisan queue:restart`; systemd relaunches with fresh code.
10. **Backups & probes** (manual) — deploy.sh snapshots the DB before each migration locally; add an **off-server** nightly `mysqldump` + remote copy (local backups don't survive a dead server), and point an external uptime probe at `/up`.

## Multi-app runner note

GitHub self-hosted runners are per-repo: hosting a second app's CI/deploy on the same VPS means installing a second runner instance (each ~1 process; label them per app or share labels deliberately).

## Verification checklist

- [ ] `bash -n deploy/provision.sh` passes; `grep -n '{{' deploy/` finds nothing
- [ ] Re-running provision.sh changes nothing (idempotent)
- [ ] Before/after `dpkg -l 'php*' nodejs` identical for already-installed packages
- [ ] Other apps still answer 200 on `/up`; their deploys still pull (`~deploy/.ssh/config` only gained a block)
- [ ] `sudo -u deploy crontab -l` still lists every other app's `schedule:run` line plus exactly one for this app
- [ ] `stat -c '%a %U:%G' /var/www/{{APP_SLUG}}/.env` → `640 deploy:www-data`, `APP_KEY=base64:…` present
- [ ] `/up` returns 200 over HTTPS; cookies secure; `systemctl status {{APP_SLUG}}-queue` active
- [ ] Deploy user can: pull, build, reload FPM — and nothing else via sudo
- [ ] A restore from the off-server backup has been tested once

## Reference implementation

Missions Solidarité Liban: `deploy/provision.sh` in `joe17xe/Msl-website` (PR #2 fixed the four shared-server bugs above on a live multi-app VPS). OrthoZ: `DEPLOYMENT.md` §1–2 and §7, `deploy/nginx.conf.example`, `deploy/orthoz-queue.service`.
