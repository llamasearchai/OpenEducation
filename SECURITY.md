# Security Policy

Supported versions

- Public beta; we aim to fix critical issues rapidly.

Reporting a vulnerability

- Please open a private security advisory on GitHub or email the maintainer.
- Do not open public issues for vulnerabilities.

Secrets hygiene

- Never commit secrets. Use environment variables or `.env` (which is gitignored).
- Use `make check-secrets` before pushing.
