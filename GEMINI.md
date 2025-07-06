### environment
- **Use gemini-2.5-pro** as primary model

### 🔄 Project Awareness & Context
- **Use consistent naming conventions, file structure, and architecture patterns.**
- **Use PRPs (Product Requirement Prompts)**: These are detailed and comprehensive feature requests that will serve as the primary mechanism for defining and guiding development tasks. They will contain all necessary context, constraints, and acceptance criteria for a given component or feature.

### 🚀 Project Phases
This project will proceed in two distinct phases:
1.  **Planning Phase**: During this phase, we will flesh out the project's details, context, and constraints. This involves defining the overall architecture, identifying key components, and creating detailed PRPs for each.
2.  **Implementation Phase**: Once the planning is complete, we will begin writing code. Development will be component-by-component, guided by the PRPs defined in the planning phase.

### 🧱 Code Structure & Modularity

### 🧱 Code Structure & Modularity
- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
  For agents this looks like:
    - `agent.py` - Main agent definition and execution logic 
    - `tools.py` - Tool functions used by the agent 
    - `prompts.py` - System prompts
- **Use clear, consistent imports** (prefer relative imports within packages).
- **Use python_dotenv and load_env()** for environment variables.

### 🧪 Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case

### ✅ Task Completion
- **After completing a task and ensuring all tests pass, perform a git commit.**
- **Mark completed tasks** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development.

### 📎 Style & Conventions
- **Use Python** as the primary language.
- **Follow PEP8**, use type hints, and format with `black`.
- **Use `pydantic` for data validation**.
- Write **docstrings for every function** using the Google style:
  ```python
  def example():
      """
      Brief summary.

      Args:
          param1 (type): Description.

      Returns:
          type: Description.
      """
  ```

### 📚 Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

### 🧠 AI Behavior Rules
- **Do not automatically start a new task.** Instead, present the task list and suggest the next step.
- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to.
