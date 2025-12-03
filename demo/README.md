# Dir2md demo (Gradio)

- Current SDK: **5.45.0** (pinned via Hugging Face metadata).
- Note: A newer Gradio SDK (**6.0.2**) is available. To try it:
  1) Update `sdk_version` in the root README front-matter.
  2) Pin `gradio==6.0.2` in `demo/requirements.txt` and redeploy the Space.
- App entrypoint: `demo/app.py`.
- Runtime deps: `gradio`, `pathspec>=0.12.0`, `GitPython`.
