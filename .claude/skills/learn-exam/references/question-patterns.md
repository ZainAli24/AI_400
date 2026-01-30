# Question Generation Patterns

## Question Types by Learning Objective

### 1. Conceptual Understanding

**Pattern**: "What does X do?" / "What is the purpose of X?"

```
Question: "What does `call_next(request)` do?"
Options:
- Sends request back to client
- Passes request to next middleware or route (correct)
- Logs the request
- Validates request data
```

**When to use**: Core concepts, function purposes, terminology

### 2. Behavioral/Consequence

**Pattern**: "What happens if/when...?"

```
Question: "If you remove `return response` from middleware, what happens?"
Options:
- Nothing, it's optional
- Client receives null
- Client gets no response (likely error) (correct)
- FastAPI auto-returns it
```

**When to use**: Error scenarios, missing code, edge cases

### 3. Execution Order/Flow

**Pattern**: "What order...?" / "When does X execute?"

```
Question: "What order do these middleware execute?"
Options:
- First defined runs first
- Last defined runs first (correct)
- Alphabetical order
- Random order
```

**When to use**: Middleware, lifecycle hooks, async operations

### 4. Type/Object Knowledge

**Pattern**: "What type is X?" / "What kind of object...?"

```
Question: "What type of object is `response` in middleware?"
Options:
- A dictionary
- A string
- A Request object
- A Response object (correct)
```

**When to use**: Return types, parameter types, object models

### 5. Best Practice/Why

**Pattern**: "Why is X done this way?" / "What's the best approach?"

```
Question: "Why use `request.state` instead of modifying headers?"
Options:
- Headers are read-only after receipt (correct)
- It's faster
- Headers don't exist in middleware
- No reason, both work the same
```

**When to use**: Design decisions, conventions, patterns

### 6. Capability/Limitation

**Pattern**: "Can you...?" / "Is it possible to...?"

```
Question: "Can you modify the request object in middleware?"
Options:
- No, request is immutable
- Yes, but only headers
- Yes, you can modify request.state (correct)
- Yes, everything is modifiable
```

**When to use**: API capabilities, language features, constraints

---

## Writing Good Wrong Answers (Distractors)

### Plausible Distractors

Wrong answers should be BELIEVABLE:

| Good Distractor | Why It Works |
|-----------------|--------------|
| Related concept | Tests if they confuse similar things |
| Common misconception | Tests if they've truly understood |
| Partially correct | Tests depth of understanding |
| Opposite behavior | Tests if they know the actual behavior |

### Bad Distractors

Avoid obviously wrong answers:

| Bad Distractor | Problem |
|----------------|---------|
| "It crashes the computer" | Too extreme |
| "Random things happen" | Too vague |
| Joke answers | Wastes an option |
| Completely unrelated | Too easy to eliminate |

---

## Question Complexity Levels

### Level 1: Recall
- Direct from code/docs
- Single concept
- "What is X?"

### Level 2: Understanding
- Apply concept
- Predict behavior
- "What happens when...?"

### Level 3: Analysis
- Compare options
- Identify relationships
- "Why X instead of Y?"

### Level 4: Synthesis
- Combine concepts
- Edge cases
- "If A and B, then what?"

**Recommended mix**: 20% L1, 40% L2, 30% L3, 10% L4

---

## Generating from Code

When analyzing user's code, look for:

| Code Pattern | Question Opportunity |
|--------------|---------------------|
| Decorators | What does this decorator do? |
| Function parameters | What type/purpose is this param? |
| Return statements | What does this return? |
| Control flow | When does this branch execute? |
| Error handling | What happens if X fails? |
| Async/await | What's the execution order? |
| Imports | What does this import provide? |
| Comments | Why is this done this way? |

---

## Option Label Guidelines

| Good | Bad |
|------|-----|
| "Passes to next handler" | "It passes the request object to the next middleware function in the chain" |
| "Returns a Response" | "The function returns a Starlette Response object type" |
| "Headers are read-only" | "Headers cannot be modified because they are immutable after the request is received" |

**Rule**: Labels ≤ 5 words. Use description field for detail.
