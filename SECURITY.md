# Security

Do not include production credentials, configuration backups, customer names, public IP addresses, or private network data in issues.

The Starter kit reads credentials from environment variables by default. For production environments, enable strict SSH host-key checking (`ssh_strict: true`) after managing `known_hosts` appropriately.

If you believe you found a security issue, report it privately to the maintainer rather than opening a public issue with exploit details.

Configuration backups can themselves contain secrets or sensitive topology information. Protect the `output/` directory, exclude it from source control, and follow your organization's retention/encryption requirements.
