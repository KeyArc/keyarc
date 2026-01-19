# Audit Logging Requirements

Every secret access must be logged.

## What to Log
- user_id (who)
- action ('secret.view', 'secret.create', 'secret.update', 'secret.delete', 'secret.share')
- resource_id (which secret)
- timestamp (when)
- ip_address (from where)

## What NOT to Log
- Secret values (plaintext or encrypted)
- Passwords or keys
- Full request/response bodies

## Retention
- 90 days minimum
- For compliance and security investigation
