# API Documentation

OneTimeSecret provides a RESTful API for creating and managing self-destructing secrets.

## Base URL

```
http://localhost:8000/api/v3
```

## Authentication

Currently, the API supports anonymous secret creation. API key authentication will be added in a future release.

## Rate Limiting

Default rate limits:
- 60 requests per minute per IP
- 1000 requests per hour per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640000000
```

## Endpoints

### Health Check

Check if the service is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "3.0.0"
}
```

---

### Create Secret

Create a new encrypted secret.

**Endpoint:** `POST /secrets`

**Request Body:**
```json
{
  "secret": "This is my secret message!",
  "passphrase": "optional-passphrase",
  "ttl": 3600,
  "burn_after_reading": true,
  "max_views": 1,
  "recipient": "john@example.com",
  "custom_message": "This is for you"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| secret | string | Yes | The secret content to encrypt (max 1MB) |
| passphrase | string | No | Optional passphrase for additional protection |
| ttl | integer | No | Time to live in seconds (default: 3600, max: 259200) |
| burn_after_reading | boolean | No | Delete after first view (default: true) |
| max_views | integer | No | Maximum number of views (default: 1, max: 100) |
| recipient | string | No | Recipient identifier (hashed, not stored as plaintext) |
| custom_message | string | No | Custom message (hashed, not stored as plaintext) |

**Response:** `201 Created`
```json
{
  "secret_id": "Xy9k2nM4pQ8rT6vZ",
  "metadata_key": "meta_Aa1Bb2Cc3Dd4Ee5Ff",
  "expires_at": "2024-01-01T12:00:00Z",
  "ttl": 3600,
  "burn_after_reading": true,
  "created_at": "2024-01-01T11:00:00Z"
}
```

**Errors:**
- `400 Bad Request` - Invalid input
- `413 Payload Too Large` - Secret exceeds size limit
- `429 Too Many Requests` - Rate limit exceeded

---

### Retrieve Secret

Retrieve and decrypt a secret. By default, this burns the secret (deletes it).

**Endpoint:** `POST /secrets/{secret_id}`

**Request Body (optional):**
```json
{
  "passphrase": "my-passphrase"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| passphrase | string | No | Required if secret has passphrase protection |

**Response:** `200 OK`
```json
{
  "secret_id": "Xy9k2nM4pQ8rT6vZ",
  "secret": "This is my secret message!",
  "burn_after_reading": true
}
```

**Errors:**
- `401 Unauthorized` - Invalid passphrase
- `404 Not Found` - Secret not found or already burned
- `410 Gone` - Secret expired or view limit reached

---

### Get Secret Metadata

Get information about a secret without burning it.

**Endpoint:** `GET /secrets/{secret_id}/metadata`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| metadata_key | string | Yes | Metadata key from secret creation |

**Response:** `200 OK`
```json
{
  "secret_id": "Xy9k2nM4pQ8rT6vZ",
  "created_at": "2024-01-01T11:00:00Z",
  "expires_at": "2024-01-01T12:00:00Z",
  "ttl": 3600,
  "is_expired": false,
  "view_count": 0,
  "max_views": 1,
  "can_view": true,
  "burn_after_reading": true,
  "passphrase_required": false
}
```

**Errors:**
- `404 Not Found` - Metadata not found

---

### Delete Secret

Manually delete a secret before it expires.

**Endpoint:** `DELETE /secrets/{secret_id}`

**Response:** `204 No Content`

**Errors:**
- `404 Not Found` - Secret not found
- `403 Forbidden` - Not authorized (if owned by another user)

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "detail": "Additional error details (optional)"
}
```

### Common HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success with no response body
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication failed
- `403 Forbidden` - Not authorized
- `404 Not Found` - Resource not found
- `410 Gone` - Resource expired or burned
- `413 Payload Too Large` - Request too large
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Examples

### Python

```python
import requests

# Create a secret
response = requests.post(
    "http://localhost:8000/api/v3/secrets",
    json={
        "secret": "My secret message",
        "ttl": 3600,
        "burn_after_reading": True
    }
)
secret_id = response.json()["secret_id"]

# Retrieve the secret
response = requests.post(
    f"http://localhost:8000/api/v3/secrets/{secret_id}"
)
secret = response.json()["secret"]
print(secret)  # "My secret message"
```

### curl

```bash
# Create a secret
curl -X POST http://localhost:8000/api/v3/secrets \
  -H "Content-Type: application/json" \
  -d '{"secret": "My secret", "ttl": 3600}'

# Retrieve the secret
curl -X POST http://localhost:8000/api/v3/secrets/Xy9k2nM4pQ8rT6vZ

# Get metadata
curl "http://localhost:8000/api/v3/secrets/Xy9k2nM4pQ8rT6vZ/metadata?metadata_key=meta_Aa1Bb2Cc3Dd4Ee5Ff"

# Delete secret
curl -X DELETE http://localhost:8000/api/v3/secrets/Xy9k2nM4pQ8rT6vZ
```

### JavaScript

```javascript
// Create a secret
const response = await fetch('http://localhost:8000/api/v3/secrets', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    secret: 'My secret message',
    ttl: 3600,
    burn_after_reading: true
  })
});
const { secret_id } = await response.json();

// Retrieve the secret
const secretResponse = await fetch(
  `http://localhost:8000/api/v3/secrets/${secret_id}`,
  { method: 'POST' }
);
const { secret } = await secretResponse.json();
console.log(secret);
```

## Interactive Documentation

When running in development mode, interactive API documentation is available:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Versioning

The API uses URL versioning (e.g., `/api/v3/`). Breaking changes will result in a new version.

Current version: **v3**

## Support

For API issues or questions:
- GitHub Issues: https://github.com/onetimesecret/ots5/issues
- Email: support@onetimesecret.com
