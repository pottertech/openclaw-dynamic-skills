---
name: systems-architect
description: System design, architecture patterns, and infrastructure planning. Use when designing new systems, evaluating architectures, planning infrastructure, or making technology decisions.
---

# Systems Architect

Professional system design and architecture guidance for scalable, reliable, and secure systems.

## When to Use

- Designing new systems or services
- Evaluating architecture options
- Planning infrastructure
- Making technology decisions
- Scaling existing systems
- Security architecture review
- Database design decisions
- API design patterns

## System Design Principles

### Core Principles

**1. Scalability**
- Design for 10x growth from day one
- Stateless services for horizontal scaling
- Database read replicas for read-heavy workloads
- Caching layers (Redis, Memcached)
- CDN for static assets

**2. Reliability**
- Redundancy at every layer
- Failover mechanisms
- Health checks and circuit breakers
- Graceful degradation
- Monitoring and alerting

**3. Security**
- Defense in depth
- Zero trust architecture
- Principle of least privilege
- Encryption at rest and in transit
- Regular security audits

**4. Maintainability**
- Clear separation of concerns
- Documentation (ADR, diagrams)
- Automated testing
- CI/CD pipelines
- Observability (logs, metrics, traces)

## Architecture Patterns

### Monolithic Architecture

**Best For:**
- Small teams (<10 engineers)
- Simple domains
- Early-stage products
- Tight coupling requirements

**Pros:**
- Simple to develop and test
- Easy deployment
- Clear transaction boundaries
- Lower operational overhead

**Cons:**
- Hard to scale components independently
- Single point of failure
- Technology lock-in
- Slower iteration as team grows

### Microservices Architecture

**Best For:**
- Large teams (>20 engineers)
- Complex domains
- Independent scaling needs
- Multiple deployment frequencies

**Pros:**
- Independent scaling
- Technology diversity
- Fault isolation
- Team autonomy

**Cons:**
- Operational complexity
- Distributed tracing needed
- Data consistency challenges
- Network latency

**Key Patterns:**
```
API Gateway → Service Mesh → Individual Services
     ↓              ↓                ↓
  Routing      Discovery        Business Logic
  AuthZ        Rate Limit       Databases
```

### Event-Driven Architecture

**Best For:**
- Real-time processing
- Decoupled systems
- High throughput
- Async workflows

**Components:**
- Event producers
- Event brokers (Kafka, RabbitMQ, SNS/SQS)
- Event consumers
- Event store (optional)

**Patterns:**
- Event sourcing
- CQRS (Command Query Responsibility Segregation)
- Saga pattern for distributed transactions

### Serverless Architecture

**Best For:**
- Sporadic traffic
- Cost optimization
- Rapid prototyping
- Event-driven workflows

**Pros:**
- No server management
- Auto-scaling
- Pay per execution
- Fast deployment

**Cons:**
- Cold starts
- Vendor lock-in
- Limited execution time
- Debugging complexity

## Database Design

### SQL vs NoSQL

| Criteria | SQL (PostgreSQL, MySQL) | NoSQL (MongoDB, DynamoDB) |
|----------|------------------------|---------------------------|
| **Data Model** | Structured, relational | Flexible, document/key-value |
| **Transactions** | ACID compliant | BASE, eventual consistency |
| **Scaling** | Vertical, read replicas | Horizontal sharding |
| **Schema** | Fixed, migrations needed | Dynamic, schema-less |
| **Best For** | Financial, complex queries | Content, high write volume |

### Database Patterns

**Read Replicas:**
```
Primary (writes) → Replica 1 (reads)
                → Replica 2 (reads)
                → Replica 3 (analytics)
```

**Sharding Strategies:**
- Horizontal (by user_id, region)
- Vertical (by feature/domain)
- Directory-based (lookup service)

**Caching Layers:**
```
Application → Redis/Memcached → Database
              (cache hit)       (cache miss)
```

## API Design

### REST Best Practices

**Resource Naming:**
```
✅ GET /users
✅ GET /users/123
✅ POST /users
✅ PUT /users/123
✅ DELETE /users/123
❌ GET /getUsers
❌ POST /createUser
```

**Status Codes:**
- 200 OK - Success
- 201 Created - Resource created
- 400 Bad Request - Invalid input
- 401 Unauthorized - Authentication needed
- 403 Forbidden - No permission
- 404 Not Found - Resource missing
- 429 Too Many Requests - Rate limited
- 500 Internal Server Error - Server issue

**Versioning:**
```
✅ /api/v1/users
✅ Accept: application/vnd.api+json; version=1
❌ /api/users_v1
```

### GraphQL

**When to Use:**
- Complex data requirements
- Multiple client types
- Reduce over-fetching
- Rapid iteration

**Schema Design:**
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
}
```

### gRPC

**When to Use:**
- Internal service communication
- High performance needs
- Strong typing required
- Streaming needed

## Infrastructure as Code

### Terraform Basics

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"
  
  tags = {
    Name        = "web-server"
    Environment = "production"
  }
}

resource "aws_security_group" "web_sg" {
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### Best Practices

- Version control all infrastructure
- Use modules for reusability
- State file management (remote backend)
- Plan before apply
- Tag all resources
- Separate environments (dev/staging/prod)

## Security Architecture

### Zero Trust Model

**Principles:**
- Never trust, always verify
- Least privilege access
- Micro-segmentation
- Continuous verification

**Implementation:**
- Identity-aware proxies
- Multi-factor authentication
- Device verification
- Encrypted communications

### Defense in Depth

```
Layer 1: Network Security (Firewall, WAF)
Layer 2: Application Security (Input validation, Auth)
Layer 3: Data Security (Encryption, Access control)
Layer 4: Monitoring (Logs, Alerts, SIEM)
```

### Security Checklist

- [ ] HTTPS everywhere
- [ ] Authentication (OAuth2, JWT)
- [ ] Authorization (RBAC, ABAC)
- [ ] Input validation
- [ ] Output encoding
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Logging and monitoring
- [ ] Secret management
- [ ] Regular security audits

## Performance & Scaling

### Scaling Strategies

**Vertical Scaling:**
- More CPU/RAM
- Limited by hardware
- Quick win, expensive

**Horizontal Scaling:**
- More instances
- Requires stateless design
- Better long-term

**Caching:**
- Application cache (in-memory)
- Distributed cache (Redis)
- CDN for static assets
- Database query cache

### Performance Optimization

**Database:**
- Index optimization
- Query optimization
- Connection pooling
- Read replicas

**Application:**
- Async processing
- Background jobs
- Lazy loading
- Pagination

**Network:**
- CDN
- Compression (gzip, brotli)
- HTTP/2
- Connection keep-alive

## Documentation

### Architecture Decision Records (ADR)

**Template:**
```markdown
# ADR-001: Database Selection

## Status
Accepted

## Context
We need to choose a database for user data storage.

## Decision
Use PostgreSQL for ACID compliance and complex queries.

## Consequences
- Pros: Transactions, complex queries, mature ecosystem
- Cons: Scaling requires more effort than NoSQL
```

### Architecture Diagrams

**Tools:**
- Draw.io (free, versatile)
- Lucidchart (collaborative)
- Excalidraw (hand-drawn style)
- Mermaid (code-based)

**Views to Document:**
- System context diagram
- Container diagram
- Component diagram
- Deployment diagram

## Trade-off Analysis

### Framework

**1. Identify Options**
- List all viable alternatives

**2. Define Criteria**
- Cost, performance, scalability, complexity

**3. Evaluate Each Option**
- Score against criteria

**4. Document Decision**
- Why chosen, why others rejected

**5. Review Periodically**
- Revisit as requirements change

### Example: Database Selection

| Criteria | PostgreSQL | MongoDB | DynamoDB |
|----------|------------|---------|----------|
| **Cost** | Low | Medium | High (at scale) |
| **Performance** | Good reads | Good writes | Excellent scale |
| **Complexity** | Medium | Low | Low |
| **Transactions** | Full ACID | Limited | Limited |
| **Decision** | ✅ Winner | - | - |

## Resources

- **Books:** "Designing Data-Intensive Applications", "Building Microservices"
- **Patterns:** microservices.io, enterprise-patterns.com
- **Tools:** Terraform, Kubernetes, Kafka, PostgreSQL
- **Monitoring:** Prometheus, Grafana, Datadog

## Examples

**Input:** "Design a URL shortener service"

**Output:**
```
1. Requirements: 100M URLs, 10:1 read/write, 5-year expiry
2. API: POST /shorten, GET /{code}, GET /{code}/stats
3. Database: PostgreSQL with read replicas
4. Cache: Redis for hot URLs
5. ID Generation: Base62 encoding of auto-increment ID
6. Scaling: Horizontal app servers, DB sharding by user_id
```

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*  
*Status: Production Ready*
