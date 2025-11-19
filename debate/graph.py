from langgraph.graph import StateGraph, START, END
from debate.state import DebateState
from debate.nodes import stance_generator, debater_a, debater_b, rebuttal_a, rebuttal_b, judge, assemble_output
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

def build_graph():

    graph = StateGraph(DebateState)

    graph.add_node("stances", stance_generator)
    graph.add_node("debater_a", debater_a)
    graph.add_node("debater_b", debater_b)
    graph.add_node("rebuttal_a", rebuttal_a)
    graph.add_node("rebuttal_b", rebuttal_b) 
    graph.add_node("judge", judge)
    graph.add_node("assemble", assemble_output)

    graph.add_edge(START, "stances")
    graph.add_edge("stances", "debater_a")
    graph.add_edge("stances", "debater_b")
    graph.add_edge("debater_a", "rebuttal_a")
    graph.add_edge("debater_b", "rebuttal_b")
    graph.add_edge("rebuttal_a", "judge")
    graph.add_edge("rebuttal_b", "judge")
    graph.add_edge("judge", "assemble")
    graph.add_edge("assemble", END)

    return graph

def get_compiled_graph():
    conn = sqlite3.connect(database="memory.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn=conn)
    
    return build_graph().compile(checkpointer=checkpointer)