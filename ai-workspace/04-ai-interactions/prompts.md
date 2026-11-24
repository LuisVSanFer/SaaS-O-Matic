
# AI Interaction and Prompt Strategy

## 1. Purpose

This document describes how AI tools are used throughout the development of SaaS-O-Matic.

AI is integrated into the development workflow as an engineering assistant, supporting requirements analysis, architectural design, technical decisions, implementation, and quality assurance.

The goal is not to delegate the entire development process to AI, but to use it to improve productivity while maintaining human supervision and technical control.

## 2. AI Usage Principles

The following principles guide AI-assisted development:

- **Human supervision:** All AI-generated proposals, code, and technical decisions must be reviewed before acceptance.
- **Incremental development:** Tasks are divided into small, manageable steps rather than requesting entire application implementations at once.
- **Specification-driven implementation:** Development tasks must follow the requirements, architecture, and specifications documented in the project.
- **Technical understanding:** AI-generated solutions must be understood and evaluated before being integrated.
- **Consistency:** AI-generated code must follow the established architecture, naming conventions, and project structure.
- **Verification:** Generated code must be validated through testing, execution, and code review.

## 3. AI-Assisted Development Workflow

AI assistance is integrated into the following stages:

| Stage | AI Contribution | Human Responsibility |
|---|---|---|
| Requirements Analysis | Identify functional requirements, ambiguities, and constraints | Review and approve requirements |
| Architecture Design | Suggest technologies, components, and architectural structures | Evaluate and select the architecture |
| Specification Design | Define module behavior, API contracts, and acceptance criteria | Validate business rules and technical details |
| Implementation | Generate code suggestions and explain implementation approaches | Review, understand, and integrate code |
| Testing | Suggest test cases and identify potential edge cases | Execute tests and evaluate results |
| Documentation | Help create and maintain technical documentation | Verify accuracy and completeness |

## 4. Prompt Design Strategy

Prompts should provide enough context for the AI to generate relevant and consistent results.

Whenever possible, development prompts should include:

1. **Project context:** A brief description of SaaS-O-Matic and its architecture.
2. **Task objective:** The specific functionality or problem to address.
3. **Technical constraints:** Required technologies, libraries, and implementation rules.
4. **Relevant specifications:** The requirements and module specifications that apply.
5. **Expected output:** The code, explanation, tests, or documentation requested.
6. **Limitations:** Explicit instructions about what should not be changed or implemented.

Tasks should be sufficiently specific to make the generated output easy to review and validate.

## 5. Representative Prompt Templates

The following templates illustrate the prompting strategy used during development. They are examples and should be adapted to the actual task and project state.

### 5.1. Requirements Analysis

**Objective:** Identify missing information and clarify business rules.

```text
Act as a software requirements engineering assistant.

Analyze the requirements for SaaS-O-Matic.

Identify:
- Functional requirements.
- Non-functional requirements.
- Business rules.
- Ambiguities and missing information.
- Potential technical constraints.

Do not make assumptions without explicitly identifying them.

Present your findings in a structured format suitable for
technical documentation.
```

### 5.2. Architecture Design

**Objective:** Evaluate architectural decisions and define component responsibilities.

```text
Act as a software architect.

Based on the approved SaaS-O-Matic requirements, propose an
architecture using:

- Python and FastAPI for the backend.
- React and TypeScript for the frontend.
- SQLite for persistence.
- SQLAlchemy as the ORM.
- Pydantic for data validation.

Define component responsibilities, communication flows,
and architectural boundaries.

Do not introduce additional technologies without explaining
their purpose and benefits.
```

### 5.3. Feature Implementation

**Objective:** Implement a feature according to its specification.

```text
Act as a senior Python developer.

Implement the requested SaaS-O-Matic functionality using
the existing project architecture.

Before generating code:
1. Review the relevant specification.
2. Identify the files that need to be created or modified.
3. Explain the proposed implementation.
4. Identify potential edge cases.

Requirements:
- Follow the documented architecture.
- Keep business logic separate from API endpoints.
- Use type hints.
- Include appropriate error handling.
- Make the implementation testable.

Do not modify unrelated modules or introduce unnecessary
dependencies.
```

### 5.4. Test Design

**Objective:** Identify relevant test cases for a module.

```text
Act as a software testing engineer.

Review the specification and implementation of the requested
SaaS-O-Matic module.

Identify:
- Expected behavior.
- Valid input cases.
- Invalid input cases.
- Boundary conditions.
- Potential edge cases.
- Relevant integration tests.

Propose automated tests using Pytest.

Do not assume that the implementation is correct simply
because it follows the specification.
```

### 5.5. Code Review

**Objective:** Review implementation quality and identify defects.

```text
Act as a senior software engineer performing a code review.

Review the provided SaaS-O-Matic implementation.

Evaluate:
- Correctness.
- Compliance with the specifications.
- Maintainability.
- Separation of concerns.
- Error handling.
- Security considerations.
- Potential edge cases.

Prioritize findings by severity.

Explain why each issue matters and suggest concrete
improvements.

Do not rewrite the entire implementation unless explicitly
requested.
```

## 6. AI Output Validation

AI-generated content must be reviewed before being accepted into the project.

The validation process includes:

- Checking compliance with documented requirements and specifications.
- Verifying technical correctness.
- Reviewing assumptions and potential inconsistencies.
- Executing relevant automated tests.
- Checking integration with existing modules.
- Ensuring that generated code does not introduce unnecessary complexity.

AI-generated code must not be considered correct solely because it executes without errors.

## 7. Traceability and Documentation

Important AI-assisted decisions and development activities must be documented.

The `development-log.md` file will record significant interactions, implementation milestones, technical decisions, problems identified, and their resolutions.

This provides traceability between requirements, AI assistance, implementation, and validation.

## 8. Continuous Improvement

The prompting strategy may evolve as the project develops.

Prompts should become more specific as the architecture and implementation mature.

Lessons learned from incorrect suggestions, failed implementations, and testing results should be used to improve subsequent interactions.
```
