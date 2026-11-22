# Security

Do not post credentials, private customer data, exploit details, or sensitive logs in public issues. If this repository offers GitHub private vulnerability reporting, use its Security tab. Otherwise contact the repository owner through a private channel you already trust before sharing details; no dedicated security mailbox or response SLA is published.

Include the affected commit, deployment mode, a minimal reproduction, impact, and relevant sanitized logs. Do not test against someone else's repository, model account, or infrastructure without authorization.

The default application is a trusted single-workspace service. Production startup validates credentials and hosts; the optional tenant gateway adds logical database separation and bearer roles. Individual SSO, hard provider quotas, stronger infrastructure isolation and independently enforced verifier receipts are not completed controls. See [readiness](docs/READINESS.md) and [integration boundaries](docs/INTEGRATIONS.md).

Keep the control plane separate from privileged execution hosts. Do not mount a Docker socket into the control-plane container. Terminate TLS at controlled ingress, keep secrets outside prompts/sandboxes, monitor failures and usage, and rehearse restoration. Update dependencies and rebuild deployed images after reviewing advisories.
