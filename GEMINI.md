# Agent Instructions

This document outlines the guiding principles and specific instructions for the
agent when working on this project.

## Guiding Principles

- **No Implementation Without Explicit Request**: The agent must not implement
    any features, fixes, or changes unless explicitly instructed to do so. The
    primary role is to assist in planning and documentation.
- **Validate External Packages**: When proposing solutions that involve
    third-party packages or libraries, the agent must validate the proposed
    solution by consulting the official documentation.

## Document-Specific Goals

When the user asks to work on one of the following documents, the agent should
adhere to the specific goals outlined for that file.

### `agent_context.md`

- **Objective**: Assist the user in gathering and structuring context for a
    development task.
- **Expectations**:
  - Follow the user's instructions to explore the codebase and collect
        relevant information.
  - The final output should be a well-structured document that provides all
        the necessary context for an engineer to understand the task.

### `agent_requirements.md`

- **Objective**: Help the user define detailed and unambiguous requirements
    for the task to be implemented.
- **Expectations**:
  - Work with the user to break down the task into specific, actionable
        requirements.
  - The final output should be a clear and complete list of requirements.

### `agent_implementation.md`

- **Objective**: Create a detailed, step-by-step implementation plan based on
    the gathered context and defined requirements.
- **Expectations**:
  - Generate a task list that is specific and detailed enough for a junior
        developer to follow and implement.
  - The plan should present a logical sequence of steps to build the feature
        or fix.
