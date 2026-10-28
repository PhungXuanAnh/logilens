# Domain recovery

The owner-maintained domain recovery bundle is stored in Dropbox:

```text
~/Dropbox/Work/infrastructure/domains/README.md
~/Dropbox/Work/infrastructure/domains/xuananh1.site/
```

Open the top-level README for the index, then `xuananh1.site/DOMAIN-USAGE.md` for the hostname-to-repository mapping, application settings and connector management links. `xuananh1.site/README.md` explains registrar transfers, new-domain migration and verification. The inventory was audited on 2026-10-28; refresh it before applying changes.

## This repository

| Hostname | Settings to review when changing the domain |
|---|---|
| `logilens.xuananh1.site` | deployment PUBLIC_ORIGIN and frontend build argument NEXT_PUBLIC_API_URL |
| `spaceship.xuananh1.site` | legacy DOMAIN_NAME in local .env; absent from the audited DNS zone |

The documented live demo uses plain HTTP on port 8899. Frontend URLs may be embedded at build time. Check the running deployment before using deploy/ EC2 templates: they differ from the documented VM deployment. Also review deploy/.env, .env.template, infra/main.tf, README links and external demo references.

## Migration and maintenance

Keeping the domain while changing registrar generally preserves application URLs when the authoritative DNS provider and nameservers remain unchanged. Buying a different domain requires reviewing DNS, tunnel routes, application settings, connectors and client links.

The Dropbox bundle includes `inventory.json`, `dependencies.json` and `prepare-domain.py`. Run the script with the new apex domain to generate a plan for review; it does not apply changes. Resolve all listed blockers before deployment.

After changing a hostname or connector, update the Dropbox inventory and this repository's links. Keep credentials in the existing secret store; the shared recovery documents contain no token or password values.
