# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |

## Security Features

OneTimeSecret implements multiple layers of security:

### Encryption
- **Fernet Symmetric Encryption**: AES-128-CBC with HMAC for authenticated encryption
- **PBKDF2 Key Derivation**: 100,000 iterations of SHA-256 for key derivation
- **Unique Salts**: Every secret uses a unique random salt
- **Secure Token Generation**: Uses Python's `secrets` module for cryptographic randomness

### Authentication & Authorization
- **Passphrase Protection**: Optional additional layer of authentication
- **API Key Support**: Secure API key authentication for programmatic access
- **Constant-Time Comparison**: Prevents timing attacks

### Data Protection
- **Zero Plaintext Storage**: Secrets are never stored unencrypted
- **No Logging**: Sensitive data never appears in logs
- **Burn After Reading**: Automatic deletion after first view
- **Configurable TTL**: Time-based expiration (5 minutes to 3 days)

### Network Security
- **SSL/TLS Required**: Enforced in production deployments
- **Security Headers**: HSTS, X-Frame-Options, CSP, X-Content-Type-Options
- **CORS Configuration**: Strict origin policies
- **Rate Limiting**: Protection against brute force and DoS attacks

### Input Validation
- **Pydantic Schemas**: Type-safe request/response validation
- **Size Limits**: Maximum secret size enforcement (1MB default)
- **TTL Validation**: Enforced time-to-live boundaries
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy ORM

### Infrastructure Security
- **Non-Root Containers**: Docker containers run as non-root user
- **Dependency Scanning**: Automated vulnerability scanning
- **Security Linting**: Bandit static analysis
- **Minimal Attack Surface**: Slim container images

## Threat Model

### In Scope
- Secret encryption/decryption
- API authentication and authorization
- Data storage and transmission
- Session management
- Rate limiting and DoS protection

### Out of Scope
- Physical security of hosting infrastructure
- Client-side security (browser, OS)
- Network infrastructure (firewalls, IDS)
- Third-party services (PostgreSQL, Redis)

### Assumptions
- Database and Redis are secured and trusted
- Network traffic is encrypted (TLS)
- Server operating system is hardened
- Environment variables are protected

## Known Limitations

1. **Metadata Leakage**: While secret content is encrypted, metadata (creation time, access patterns) is visible to database administrators
2. **Memory Exposure**: Decrypted secrets exist briefly in application memory
3. **No Perfect Forward Secrecy**: Compromise of SECRET_KEY allows decryption of all stored secrets
4. **Timing Attacks**: While mitigated, sophisticated timing attacks may be possible
5. **Redis Security**: Session data in Redis is not encrypted at rest by default

## Security Best Practices

### Deployment

1. **Generate Strong Keys**
   ```bash
   openssl rand -hex 32
   ```

2. **Enable SSL/TLS**
   ```bash
   SSL_ENABLED=true
   ```

3. **Use Strong Database Passwords**
   - Minimum 20 characters
   - Mix of letters, numbers, symbols
   - Unique per environment

4. **Restrict CORS Origins**
   ```bash
   CORS_ORIGINS=https://yourdomain.com
   ```

5. **Configure Rate Limits**
   ```bash
   RATE_LIMIT_PER_MINUTE=60
   RATE_LIMIT_PER_HOUR=1000
   ```

6. **Regular Updates**
   - Monitor for security updates
   - Update dependencies regularly
   - Review security advisories

### Operations

1. **Rotate Secrets**: Regularly rotate encryption keys (requires migration)
2. **Monitor Logs**: Watch for suspicious activity patterns
3. **Database Backups**: Encrypt database backups at rest
4. **Access Control**: Limit who can access production systems
5. **Audit Trail**: Enable database audit logging

### Development

1. **Never Commit Secrets**: Use `.env` files (gitignored)
2. **Code Review**: All changes reviewed for security issues
3. **Dependency Scanning**: Run `safety check` regularly
4. **Static Analysis**: Use bandit for security linting
5. **Update Dependencies**: Keep dependencies current

## Reporting a Vulnerability

**DO NOT** create public GitHub issues for security vulnerabilities.

### How to Report

1. **Email**: security@onetimesecret.com
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Assessment**: Within 7 days
- **Fix Timeline**: Based on severity
  - Critical: 1-7 days
  - High: 7-30 days
  - Medium: 30-90 days
  - Low: Next release

### Disclosure Policy

- We follow coordinated disclosure
- Security fixes released before public disclosure
- Credit given to reporters (unless anonymous)
- CVE assigned for significant vulnerabilities

## Security Checklist

Before deploying to production:

- [ ] Generated strong SECRET_KEY (32+ characters)
- [ ] SSL/TLS enabled (SSL_ENABLED=true)
- [ ] Production database with strong password
- [ ] Redis with authentication enabled
- [ ] CORS origins restricted to trusted domains
- [ ] Rate limiting enabled
- [ ] Debug mode disabled (DEBUG=false)
- [ ] Environment variables secured
- [ ] Database backups configured
- [ ] Monitoring and alerting set up
- [ ] Security headers verified
- [ ] Dependencies scanned for vulnerabilities
- [ ] Access logs enabled
- [ ] Firewall rules configured
- [ ] Non-root user running application

## Incident Response

In case of a security incident:

1. **Contain**: Isolate affected systems
2. **Assess**: Determine scope and impact
3. **Notify**: Contact security team
4. **Remediate**: Apply fixes
5. **Document**: Record incident details
6. **Review**: Post-incident analysis

## Security Contacts

- **Security Email**: security@onetimesecret.com
- **Maintainer**: See CODEOWNERS file

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Cryptography Library](https://cryptography.io/)

---

Last Updated: 2024-01-01
