# Ont examples

`ont.factory.json` is a minimal validated factory definition. Import it in Factory configuration or send it to the authenticated factory API. It contains a repository identifier, budget, harness label, and human approval gates. Importing it does not create a repository or configure a provider.

Use `ont demo` for a standalone labeled walkthrough. For real execution, follow [integration setup](../docs/INTEGRATIONS.md) and configure a trusted worker, repository credentials, exact checkout, and verification policy. Never store secrets in a factory definition.
