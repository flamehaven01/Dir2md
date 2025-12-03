import gradio as gr
import git
import tempfile
import shutil
from pathlib import Path
import os
import json
import sys

# Ensure local dir2md package is importable in the HF Space
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dir2md.core import generate_markdown_report, Config


def process_github_repo(
    repo_url: str,
    preset: str,
    spicy: bool,
    include_contents: bool,
    max_size_mb: int,
    shallow: bool,
):
    """
    Clone a public GitHub repository and generate dir2md outputs (human MD + AI JSONL).
    """
    temp_dir_path = None
    try:
        temp_dir_path = tempfile.mkdtemp()
        temp_dir = Path(temp_dir_path)

        gr.Info(f"Cloning repository: {repo_url} ...")
        clone_args = {"to_path": temp_dir}
        if shallow:
            clone_args["depth"] = 1
            clone_args["single_branch"] = True
        git.Repo.clone_from(repo_url, **clone_args)
        gr.Info("Repository cloned. Generating blueprint...")

        # size guard
        total_bytes = sum(f.stat().st_size for f in temp_dir.rglob("*") if f.is_file())
        total_mb = total_bytes / (1024 * 1024)
        if total_mb > max_size_mb:
            raise ValueError(f"Repository too large: ~{total_mb:.1f} MB (limit {max_size_mb} MB)")

        output_path = temp_dir / "blueprint.md"

        cfg = Config(
            root=temp_dir,
            output=output_path,
            preset=preset,
            include_globs=[],
            exclude_globs=[],
            omit_globs=[],
            respect_gitignore=True,
            follow_symlinks=False,
            max_bytes=None,
            max_lines=None,
            include_contents=include_contents,
            llm_mode="summary",  # more readable by default
            budget_tokens=8000,
            max_file_tokens=2000,
            dedup_bits=16,
            sample_head=120,
            sample_tail=40,
            strip_comments=False,
            emit_manifest=False,  # demo keeps outputs in-memory
            explain_capsule=False,
            no_timestamp=True,
            masking_mode="basic",
            spicy=spicy,
        )

        md_output = generate_markdown_report(cfg)

        # AI-friendly JSONL output: reuse cfg with jsonl
        cfg.output_format = "jsonl"
        cfg.output = temp_dir / "blueprint.jsonl"
        jsonl_output = generate_markdown_report(cfg)

        gr.Info("Blueprint generated successfully!")

        return md_output, jsonl_output

    except Exception as e:
        if temp_dir_path and os.path.exists(temp_dir_path):
            shutil.rmtree(temp_dir_path)
        return f"An error occurred: {e}", ""
    finally:
        if temp_dir_path and os.path.exists(temp_dir_path):
            shutil.rmtree(temp_dir_path)


demo = gr.Interface(
    fn=process_github_repo,
    inputs=[
        gr.Textbox(label="GitHub Repository URL", placeholder="https://github.com/Flamehaven/dir2md"),
        gr.Radio(choices=["pro", "raw"], value="pro", label="Select Preset"),
        gr.Checkbox(label="Spicy risk report", value=True),
        gr.Checkbox(label="Include file contents", value=True),
        gr.Slider(label="Max repo size (MB)", minimum=10, maximum=500, value=200, step=10),
        gr.Checkbox(label="Shallow clone (depth=1)", value=True),
    ],
    outputs=[
        gr.Textbox(label="Markdown Blueprint (human)", lines=30, show_copy_button=True),
        gr.Textbox(label="JSONL (AI-ready)", lines=15, show_copy_button=True),
    ],
    title="dir2md: AI-Ready Repository Blueprint Generator",
    description="Enter a public GitHub repository URL to convert its structure/content into a Markdown blueprint (human) and JSONL (AI).",
    allow_flagging="never",
    examples=[
        ["https://github.com/psf/requests", "pro", True, True, 200, True],
        ["https://github.com/gradio-app/gradio", "raw", True, True, 200, True],
    ],
)

demo.launch()
