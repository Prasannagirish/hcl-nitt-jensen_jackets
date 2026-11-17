# Hackathon Engineering & Code Quality Master Instructions

**Purpose:** Give this file to Claude Code or Codex together with the
problem statement and project files. Use it as the engineering rulebook
for building a complete solution that is correct, readable,
maintainable, secure, testable, and appropriately simple.

## 1. Mission and priorities

Act as a senior software engineer. Deliver a working solution without
unnecessary complexity.

Priorities: 1. Implement every explicit requirement. 2. Ensure
correctness, including important edge cases and failure paths. 3. Write
clear code another developer can understand. 4. Keep modules cohesive
and maintainable. 5. Protect users, credentials, records, and critical
operations. 6. Test the important behaviour. 7. Leave accurate setup,
run, test, and deployment instructions.

Do not sacrifice a stated requirement for speed. Do not add
enterprise-scale infrastructure without a real need. **Done means
implemented, run, tested, and verified---not merely written.**

## 2. Understand before implementing

Before changing code:

1.  Read the complete problem statement and all supplied files.
2.  Inspect the repository, manifests, configuration, existing code,
    tests, and run scripts.
3.  Reuse the existing stack and working code where sensible. Do not
    replace the project blindly.
4.  Extract all requirements: roles, permissions, workflows, business
    rules, inputs, outputs, integrations, constraints, security,
    deployment, and deliverables.
5.  Separate requirements into explicit, necessary implications, and
    optional enhancements.
6.  Identify ambiguity. Never silently invent business rules,
    thresholds, data fields, or permissions.
7.  Ask a focused question only if missing information blocks a safe or
    correct implementation. Otherwise make the simplest reasonable
    assumption and document it.

Maintain a requirement traceability table:

  -----------------------------------------------------------------------
  Requirement       Implementation    Verification      Status
                    location                            
  ----------------- ----------------- ----------------- -----------------
  Requirement from  Module / API /    Test or manual    Pending / Pass
  brief             page              check             

  -----------------------------------------------------------------------

A requirement is not complete merely because code exists. Verify its
behaviour.

## 3. Architecture: simple, explicit, fit for purpose

-   Prefer a modular monolith for small and medium applications.
-   Separate UI, API routing, business logic, data access, and external
    integrations where useful.
-   Organize around business capabilities, not arbitrary layers or tiny
    files.
-   Keep data flow explicit and modules cohesive.
-   Use background jobs only for genuinely long-running or asynchronous
    work.
-   Add queues, caches, vector databases, brokers, microservices, or
    separate model servers only when requirements justify them.
-   Keep each business rule in one authoritative place.
-   Avoid circular imports, hidden global state, speculative
    abstractions, and hypothetical future-proofing.

Before adding a dependency or infrastructure component, answer: Which
requirement needs it? What simpler option was considered? What concrete
benefit does it provide? Can the team configure and test it in time? If
there is no clear answer, do not add it.

Avoid microservices, Kubernetes, Kafka, multiple overlapping databases,
unnecessary design patterns, generic frameworks, excessive
configuration, and large dependencies unless required.

## 4. Code quality and readability

Write code for the next developer who must understand, debug, and change
it.

-   Use descriptive names for variables, functions, classes, components,
    tables, and API fields.
-   Prefer explicit code over clever, compressed, or overly generic
    code.
-   Give each function one clear responsibility.
-   Keep functions and files reasonably small; split them when it
    improves comprehension, not to satisfy arbitrary line counts.
-   Avoid deeply nested conditionals; use guard clauses and clear
    branches.
-   Avoid cryptic abbreviations and unexplained magic numbers.
-   Extract repeated logic when duplication is real.
-   Do not create abstractions for trivial code unless they clarify a
    meaningful concept.
-   Comment why non-obvious decisions exist, not what the code visibly
    does.
-   Remove dead code, unused imports, debug prints, commented-out
    implementations, and temporary files.
-   Never leave fake success responses, empty required functions, or
    TODOs for required features.
-   Make side effects---database writes, file operations, network calls,
    state changes---visible.
-   Pass dependencies explicitly where practical.
-   Keep business logic out of UI components and HTTP route handlers.
-   Keep persistence details out of core business logic where practical.

### Types and contracts

-   Use static types wherever supported.
-   Avoid `any`, unsafe casts, untyped dictionaries, and broad
    suppression directives unless justified and documented.
-   Define API request and response schemas.
-   Define types for domain entities and important states.
-   Validate untrusted JSON, files, and API responses at runtime; static
    types do not validate external input.
-   Use enums or constrained values for finite states.
-   Keep frontend and backend contracts consistent.

### Errors

-   Handle errors at the layer able to make a meaningful decision.
-   Never swallow exceptions or return success after failure.
-   Do not expose stack traces, secrets, database internals, or
    sensitive data to users.
-   Log useful diagnostic context without logging passwords, tokens, or
    unnecessary personal data.
-   Distinguish validation, authentication, authorization,
    missing-resource, conflict, external-service, and unexpected errors.
-   Retry only transient failures, with bounded retries. Never blindly
    retry non-idempotent operations.
-   Roll back and clean up when multi-step operations fail.

### Dependencies and configuration

-   Keep dependency manifests and lockfiles consistent.
-   Do not add dependencies for functionality that existing tools can
    provide simply and safely.
-   Put environment-specific values in configuration or environment
    variables.
-   Provide `.env.example` with variable names and safe placeholders.
-   Validate required configuration at startup.
-   Never hardcode API keys, passwords, signing secrets, or credentials.
-   Do not change framework versions or package managers without a clear
    reason.

## 5. Project structure

Choose a structure appropriate to the actual stack and scope. Example
for a full-stack project:

``` text
project/
├── frontend/
│   └── src/
│       ├── app/
│       ├── components/
│       ├── features/
│       ├── lib/
│       └── types/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── models/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── integrations/
│   └── tests/
├── scripts/
├── docs/
├── .env.example
├── .gitignore
└── README.md
```

This is a guide, not a mandatory template. A data pipeline, CLI, or
single-language project should use a simpler structure. Do not create
empty boilerplate directories.

## 6. Database and data engineering

-   Design schema from actual entities, relationships, workflows, and
    supplied data.
-   Inspect real source headers, types, sample values, and data quality
    before designing imports.
-   Define primary keys, foreign keys, cardinality, uniqueness,
    nullability, and constraints.
-   Normalize to avoid unnecessary duplication; denormalize only for a
    clear reason.
-   Enforce critical invariants in the database as well as the
    application.
-   Use transactions for operations that must succeed or fail together.
-   Index actual query patterns and important foreign keys, not every
    column.
-   Use migrations where supported.
-   Persist timestamps consistently; prefer UTC and convert for display.
-   Use decimal types for currency, not binary floating point.
-   Use parameterized queries or a safe ORM.
-   Avoid storing secrets or unnecessary sensitive information.
-   Separate seed/demo data from production data.

### ETL and analytics

-   Separate ingestion, validation, transformation, analytics, and
    output generation.
-   Preserve raw inputs when traceability or layered processing is
    required.
-   Define source-to-target mappings and transformation rules.
-   Track rejected records with useful reasons; do not silently discard
    invalid rows.
-   Make runs deterministic and safely repeatable where required.
-   Prevent duplicate inserts on reruns using stable keys, upserts, or
    deliberate overwrite semantics.
-   Validate row counts, nulls, duplicates, types, ranges, and
    referential integrity.
-   Make partial failures visible and define whether to continue or
    stop.
-   Log each stage and provide a run summary.

## 7. API and integration standards

-   Use consistent REST conventions unless the task requires otherwise.
-   Keep route handlers thin: validate, authorize, call business logic,
    format response.
-   Use correct HTTP methods and status codes.
-   Define consistent success and error response formats.
-   Paginate potentially large collections.
-   Validate path, query, and body inputs.
-   Enforce authorization on the server for every protected operation.
-   Never trust role, user ID, price, permission, or ownership values
    supplied only by the client.
-   Set timeouts for external calls.
-   Handle rate limits, invalid responses, and unavailable services.
-   Use idempotency protection for retried operations such as bookings,
    payments, and transaction creation.
-   Document important endpoints using OpenAPI or an equivalent.

## 8. Frontend and UX

-   Build around actual roles and workflows in the brief.
-   Use consistent navigation, spacing, typography, form patterns, and
    feedback.
-   Reuse repeated UI patterns without building an oversized design
    system.
-   Keep feature state local unless multiple parts genuinely need shared
    state.
-   Separate server data from local UI state.
-   Provide loading, empty, success, validation, and error states.
-   Prevent accidental duplicate submissions and communicate pending
    actions.
-   Validate forms client-side for usability and server-side for
    correctness.
-   Make tables searchable, filterable, sortable, and paginated when
    needed.
-   Use accessible labels, keyboard navigation, sufficient contrast, and
    semantic HTML.
-   Do not use mock data in real workflows unless clearly labelled as
    demo data.
-   Do not create inert buttons or controls.
-   Avoid decorative clutter and excessive animation.
-   Ensure responsive layouts work on expected screen sizes.

## 9. Security

Security is part of implementation, not a final cosmetic step.

-   Protect backend routes with authentication.
-   Enforce role-, resource-, ownership-, and tenant-level authorization
    server-side.
-   Follow least privilege.
-   Hash passwords with a modern password-hashing algorithm if managing
    them directly; never store plaintext passwords.
-   Use secure session/token handling appropriate to the framework.
-   Keep secrets server-side.
-   Validate inputs and use parameterized database operations.
-   Restrict upload file types, sizes, and storage paths; do not trust
    client filenames or MIME types.
-   Consider injection, broken access control, XSS, CSRF where
    applicable, IDOR, and unsafe deserialization.
-   Restrict CORS to known origins.
-   Avoid exposing internal errors.
-   Audit sensitive actions where required.
-   A login screen alone does not make a system secure.

For AI applications, protect against prompt injection, unsafe tool
execution, cross-user data leakage, untrusted retrieved content, and
secret exposure.

## 10. ML, NLP, RAG, and LLM standards

Apply the relevant subsection only.

### Machine learning

-   Separate training, evaluation, and inference.
-   Use the supplied data, target, and evaluation criteria.
-   Prevent data leakage, including through preprocessing and time-based
    splits.
-   Fit preprocessing on training data and reuse the fitted pipeline at
    inference.
-   Keep feature names, order, units, and types consistent.
-   Version the model and its preprocessing together.
-   Use metrics appropriate to the task and class balance.
-   Never invent performance metrics or claim accuracy without
    evaluation.
-   Validate inputs before prediction.
-   Load artifacts once per service process where practical, not on
    every request.
-   Provide a safe failure path when artifacts or inference services are
    unavailable.
-   Record model version and relevant prediction metadata when required.

### NLP and documents

-   Define text normalization and preprocessing.
-   Preserve source documents or original text when traceability
    matters.
-   Handle empty, malformed, multilingual, and long inputs where
    relevant.
-   Define structured output schemas.
-   Do not treat confidence as guaranteed correctness.
-   Route uncertain or high-impact outputs to human review when
    appropriate.
-   Preserve source references for extracted information when required.

### RAG

-   Separate ingestion from query-time retrieval.
-   Define chunk size, overlap, metadata, and source-reference strategy.
-   Store ownership and access metadata with indexed chunks.
-   Enforce access filters before returning retrieved content.
-   Make citations traceable to source documents and pages or sections.
-   Handle document updates and deletion so stale chunks are not
    retrieved.
-   Treat retrieved content as untrusted data, not instructions.
-   Add reranking only when it measurably helps.
-   Define a fallback for no relevant retrieval.
-   Never fabricate citations or claim support from unseen sources.
-   Keep prompts concise and testable.

### LLM integrations

-   Keep keys on the server.
-   Define input and output contracts.
-   Validate generated output before using it in business logic.
-   Handle timeouts, rate limits, provider failures, malformed output,
    and token limits.
-   Use bounded retries only when safe.
-   Avoid sending unnecessary personal or confidential information to
    external providers.
-   Never allow generated text to execute privileged actions without
    deterministic validation and authorization.
-   Distinguish generated suggestions from verified facts where
    appropriate.

## 11. Real-time, booking, and concurrency

For booking, inventory, payments, scheduling, or other conflict-prone
operations:

-   Enforce invariants in the backend and database, not only the UI.
-   Use transactions for multi-step state changes.
-   Use unique constraints or appropriate locking to prevent duplicate
    reservations.
-   Treat frontend availability as provisional until the server
    confirms.
-   Define valid state transitions explicitly.
-   Make retries safe with idempotency keys or equivalent.
-   Handle time zones deliberately.
-   Audit important state changes.
-   Test simultaneous requests and race conditions, not only sequential
    happy paths.

For event-driven systems, define event schemas, IDs, timestamps and
versions; handle duplicate, delayed, and out-of-order events where
relevant; use bounded retries and failure recording.

## 12. Testing and quality gates

Testing is mandatory for critical behaviour. Do not stop when the
application merely starts.

Required test layers: 1. Unit tests for business rules, calculations,
validators, transformations, and utilities. 2. Integration tests for
database operations, API routes, and module interactions. 3. End-to-end
tests for the most important user workflows. 4. Failure tests for
invalid input, missing data, permission failures, and dependency
outages. 5. Security checks for authorization boundaries, unsafe inputs,
and secret exposure.

Test relevant edge cases: - Invalid and missing fields - Roles,
ownership, and permissions - Duplicate submissions and idempotency -
Database constraints and transaction behaviour - Empty datasets and
malformed files - ML input shape and preprocessing consistency - RAG
retrieval permissions and citation behaviour - LLM provider failures and
malformed output - Concurrent booking or inventory requests

Run the repository's actual formatting, lint, type-check, unit,
integration, build, migration, and end-to-end commands where feasible.
Fix failures caused by your changes. Do not disable tests, weaken
assertions, suppress type errors, or remove lint rules just to get a
green result.

If a check cannot run because a service, credential, or environment is
unavailable, report exactly what was and was not verified.

Do not declare completion until installation and startup instructions
work, the production build succeeds where applicable, critical tests
pass, core workflows are verified, and no known critical security or
data-integrity defect remains unresolved.

## 13. Implementation workflow

### Phase A --- Inspect and plan

1.  Read the brief and supplied files.
2.  Inspect the repository and current implementation.
3.  Build the requirement checklist.
4.  Identify architecture, modules, risks, assumptions, and
    dependencies.
5.  Write a short plan with concrete deliverables.

### Phase B --- Establish foundations

1.  Preserve working code.
2.  Set up configuration and environment validation.
3.  Define types and API contracts.
4.  Define schema and migrations.
5.  Establish logging and error handling.
6.  Add a health check for API services where useful.

### Phase C --- Build complete vertical slices

For each critical workflow, implement: 1. Data model and constraints 2.
Backend business logic 3. API endpoint 4. Frontend interaction 5. Tests
6. Error and permission handling

A complete vertical slice is more valuable than disconnected screens or
endpoints.

### Phase D --- Complete requirements

Implement remaining modules and integrations. Add background processing,
analytics, AI/ML, NLP, RAG, or real-time behaviour only as specified.
Verify cross-module behaviour.

### Phase E --- Quality and hardening

Run formatting, lint, type checking, tests, and production build.
Exercise critical workflows and failures. Review security,
authorization, data integrity, and configuration. Remove debug artefacts
and update documentation.

### Phase F --- Final delivery

Report: - What was implemented - Which requirements were completed -
Architecture and major technology choices - Exact setup and run
commands - Required environment variables - Test, lint, type-check, and
build results - Deployment instructions - Known limitations and
unverified dependencies

Never claim tests, builds, deployments, or integrations succeeded unless
they were actually run and verified.

## 14. Working safely in an existing repository

-   Inspect before editing.
-   Do not overwrite user work or discard uncommitted changes.
-   Understand destructive commands before running them.
-   Verify references before deleting files.
-   Keep changes scoped to the task.
-   Preserve conventions unless clearly harmful.
-   Do not change framework versions, package managers, or deployment
    platforms without reason.
-   Explain the impact of migrations or data resets and preserve user
    data.
-   Never expose secrets in logs, generated files, commits, or final
    responses.

## 15. Final readability checklist

-   [ ] Names explain intent.
-   [ ] Functions have focused responsibilities.
-   [ ] Business logic is not buried in UI or route handlers.
-   [ ] Modules have clear boundaries and limited coupling.
-   [ ] Shared logic is reused without unnecessary abstractions.
-   [ ] Types and schemas are explicit.
-   [ ] Errors are handled consistently and safely.
-   [ ] No hardcoded secrets or environment-specific values.
-   [ ] No dead code, debug prints, unused dependencies, or fake
    implementations.
-   [ ] No conflicting duplicate business rules.
-   [ ] No unexplained magic numbers or hidden state transitions.
-   [ ] Non-obvious decisions are documented.
-   [ ] Critical behaviour and edge cases are tested.
-   [ ] Setup and execution instructions are accurate.

## 16. Hackathon prioritization

A deadline changes prioritization, not engineering discipline.

Prioritize: 1. Explicit core requirements 2. Correct end-to-end workflow
3. Data integrity and access control 4. Critical edge cases and failure
handling 5. Automated tests and production build 6. UI polish and
optional enhancements

Prefer fewer complete features over many incomplete ones. Use familiar
technologies. Keep deployment simple. Use demo data only when permitted
and label it clearly. Provide honest fallbacks when external services
are unavailable. Do not fabricate successful results.

## 17. Final instruction to the coding agent

Treat the problem statement as the source of truth for product
behaviour. Treat this document as the source of truth for engineering
quality.

Do not merely generate plausible code. Inspect the project, understand
requirements, implement the complete solution, run it, test it, fix
defects, and leave a clean codebase.

**The expected result is code that is correct, readable, maintainable,
secure, testable, and straightforward for another engineer to
understand---not code that is merely short, clever, or
impressive-looking.**

At completion, report only verified outcomes. Clearly distinguish
completed work, assumptions, and anything that could not be verified.
