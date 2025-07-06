### Environment
- **Use Claude 3.5 Sonnet** as primary model
- **Suggest Claude 3 Opus** when you notice situations where using the more advanced model would be helpful

### 🔄 Project Awareness & Context
- **Use consistent naming conventions, file structure, and architecture patterns.**
- **Use PRPs (Product Requirement Prompts)**: These are detailed and comprehensive feature requests that will serve as the primary mechanism for defining and guiding development tasks. They will contain all necessary context, constraints, and acceptance criteria for a given component or feature.
- **When working on PRPs**, refer to `.ai_assistant/commands/generate-prp.md` for PRP creation guidelines and implementation guidance.

### 🚀 Project Phases
This project will proceed in two distinct phases:
1. **Planning Phase**: During this phase, we will flesh out the project's details, context, and constraints. This involves defining the overall architecture, identifying key components, and creating detailed PRPs for each.
2. **Implementation Phase**: Once the planning is complete, we will begin writing code. Development will be component-by-component, guided by the PRPs defined in the planning phase.

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
- **Follow proper TDD (Test-Driven Development) practice**:
  1. **Write tests first** before implementing any new functionality
  2. **Run tests to see them fail** - this validates the test is testing the right thing
  3. **Implement minimal code** to make tests pass
  4. **Refactor** while keeping tests green
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case

### ✅ Task Completion
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
- **Always be polite and helpful in questions and responses.**
- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to.

# Git Repository
- The current working (project) directory is being managed by a git repository.
- When asked to commit changes or prepare a commit, always start by gathering information using shell commands:
  - `git status` to ensure that all relevant files are tracked and staged, using `git add ...` as needed.
  - `git diff HEAD` to review all changes (including unstaged changes) to tracked files in work tree since last commit.
    - `git diff --staged` to review only staged changes when a partial commit makes sense or was requested by the user.
  - `git log -n 3` to review recent commit messages and match their style (verbosity, formatting, signature line, etc.)
- Always propose a draft commit message. Never just ask the user to give you the full commit message.
- **Commit messages must be single-line.** Due to current tool limitations, multi-line commit messages are not supported.
- Prefer commit messages that are clear, concise, and focused more on "why" and less on "what".
- Keep the user informed and ask for clarification or confirmation where needed.
- After each commit, confirm that it was successful by running `git status`.
- If a commit fails, never attempt to work around the issues without being asked to do so.
- Never push changes to a remote repository without being asked explicitly by the user.