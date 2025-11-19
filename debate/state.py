from typing_extensions import TypedDict


class DebateState(TypedDict, total=False):
    topic: str
    current_round: int


    # stances
    stance_a: str
    stance_b: str


    # opening args
    argument_a: str
    argument_b: str


    # rebuttals
    rebuttals_a: str
    rebuttals_b: str

    # verdict and final
    verdict: str
    final_markdown: str