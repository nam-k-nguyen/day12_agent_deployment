# Compatibility and Optimization Plan

## 1. Ensure Python Compatibility
- Review all code for Colab-specific constructs (e.g., file uploads, magic commands, notebook-only imports).
- Refactor any notebook-specific code to standard Python equivalents.
- Validate all imports are available in requirements.txt and compatible with server Python environments.

## 2. Optimize Heavy Model Loading
- Identify where `translate_model` and `detoxify_model` are loaded in `defense/pipeline.py`.
- Refactor code so models are loaded only once per process, not on every script run.
- Options:
  - Use a singleton pattern or module-level caching for models.
  - If running as a web service (e.g., FastAPI/Flask), load models at server startup and reuse for requests.
  - If running as a script, ensure models are not reloaded unnecessarily.

## 3. Dockerization Preparation
- Ensure all dependencies are listed in requirements.txt.
- Remove any interactive or GUI code not suitable for headless/server environments.
- Add a Dockerfile for reproducible builds.
- Test the application in a container to confirm models load only once and the app runs as expected.

## 4. Next Steps
- Refactor `pipeline.py` for model loading optimization.
- Review and update requirements.txt.
- Add Dockerfile and .dockerignore.
- Test end-to-end in Docker.
