from debate.prompts import SYSTEM_STANCE, SYSTEM_DEBATER, SYSTEM_REBUTTAL, SYSTEM_JUDGE, JUDGE_FORMAT
from debate.state import DebateState
from debate.llm import _llm
from debate.utils import format_markdown_summary


def stance_generator(state: DebateState):
    topic = state["topic"]
    chain = _llm(SYSTEM_STANCE)
    resp = chain.invoke({"input": f"Topic: {topic}\nReturn two opposing labels as 'A: ...' and 'B: ...'"})
    text = resp.content.strip()
    stance_a, stance_b = "Pro", "Con"
    # naive parse
    for line in text.splitlines():
        if line.lower().startswith("a:"):
            stance_a = line.split(":",1)[1].strip()
        if line.lower().startswith("b:"):
            stance_b = line.split(":",1)[1].strip()
    state['stance_a'] = stance_a
    state['stance_b'] = stance_b
    return {
        "stance_a": stance_a,
        "stance_b": stance_b
    }


def debater_a(state: DebateState):
    stance = state["stance_a"]
    topic = state["topic"]
    chain = _llm(SYSTEM_DEBATER)
    text = chain.invoke({
        "input": f"Debate topic: {topic}\nYour stance: {stance}\nWrite an opening argument (150-250 words)."
    })
    
    state['argument_a'] = text
    return {
    "argument_a": text.content if hasattr(text, "content") else str(text)
    }


def debater_b(state: DebateState):
    stance = state["stance_b"]
    topic = state["topic"]
    chain = _llm(SYSTEM_DEBATER)
    text = chain.invoke({
        "input": f"Debate topic: {topic}\nYour stance: {stance}\nWrite an opening argument (150-250 words)."
    })
    
    state['argument_b'] = text
    return {
    "argument_b": text.content if hasattr(text, "content") else str(text)
    }


def rebuttal_a(state: DebateState):
    chain = _llm(SYSTEM_REBUTTAL)
    text = chain.invoke({
        "input": (
            f"Topic: {state['topic']}\n"
            f"Your stance A: {state['stance_a']}\n"
            f"Opponent B's last: {state['argument_b'] if state['current_round']==0 else state['rebuttals_b']}\n"
            f"Write a concise rebuttal (80-150 words)."
        ),
        "side" : "A"
    })
    rebuttal_text = text.content if hasattr(text, "content") else str(text)
    state['rebuttals_a'] = rebuttal_text
    return {
    "rebuttals_a": rebuttal_text
    }


def rebuttal_b(state: DebateState):
    chain = _llm(SYSTEM_REBUTTAL)
    text = chain.invoke({
        "input": (
            f"Topic: {state['topic']}\n"
            f"Your stance B: {state['stance_b']}\n"
            f"Opponent A's last: {state['argument_a'] if state['current_round']==0 else state['rebuttals_a']}\n"
            f"Write a concise rebuttal (80-150 words)."
        ),
        "side" : "B"
    })
    rebuttal_text = text.content if hasattr(text, "content") else str(text)
    state['rebuttals_b'] = rebuttal_text
    return {
    "rebuttals_b": rebuttal_text
    }


def judge(state: DebateState):
    chain = _llm(SYSTEM_JUDGE)
    pack = (
        f"{JUDGE_FORMAT}"
    )
    text = chain.invoke({"input": pack})
    state['verdict'] = text
    return {
    "verdict": text.content if hasattr(text, "content") else str(text)
    }


def assemble_output(state: DebateState):
    text = format_markdown_summary(state)
    state['final_markdown'] = text
    return {
    "final_markdown": text
    }