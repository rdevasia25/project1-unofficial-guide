"""
app.py — Gradio web interface for the VT CS Professor Unofficial Guide.

Usage:
    python app.py
    # Opens at http://localhost:7860
"""

import gradio as gr

from generate import ask

EXAMPLES = [
    "Who should I take for CS1064?",
    "Does Farghally offer test retakes?",
    "Is Chris Thomas's ML class worth it?",
    "What do students say about Margaret Ellis in CS2114?",
    "How many reports does Amun Kharel assign in CS3724?",
    "What is the best dining hall near campus?",  # out-of-domain grounding test
]


def handle_query(question: str) -> tuple[str, str]:
    if not question.strip():
        return "", ""
    result = ask(question)
    sources_text = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources_text


with gr.Blocks(title="VT CS Professor Unofficial Guide") as demo:
    gr.Markdown(
        "## VT CS Professor Unofficial Guide\n"
        "Ask anything about CS professors at Virginia Tech. "
        "Answers are grounded in student reviews from Rate My Professors and Coursicle."
    )

    with gr.Row():
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. Who should I take for CS1064?",
            scale=4,
        )
        btn = gr.Button("Ask", variant="primary", scale=1)

    answer = gr.Textbox(label="Answer", lines=9, interactive=False)
    sources = gr.Textbox(label="Retrieved from", lines=3, interactive=False)

    gr.Examples(examples=EXAMPLES, inputs=inp, label="Try an example")

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

demo.launch()
