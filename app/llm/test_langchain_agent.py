import pytest

from app.llm.langchain_agent import (
    is_temporal_question,
    answer_temporal_question,
)


class FakeChain:
    def __init__(self, ressponse: str):
        self._response = ressponse
        self.last_input = None

    def invoke(self, input_dict):
        """Input debugging."""
        self.last_input = input_dict
        return self._response


class FakeDocChain:
    def __init__(self, response: str):
        self._response = response
        self.last_input = None

    def invoke(self, input_dict):
        self.last_input = input_dict
        # In the real chain, input_dict contains {"question": "..."}
        return self._response


@pytest.mark.asyncio
async def test_temporal_question_is_true():
    chain = FakeChain("YES")
    result = await is_temporal_question("How do I start a workflow in Temporal?", chain=chain)
    assert result is True
    assert "How do I start a workflow" in chain.last_input["question"]


@pytest.mark.asyncio
async def test_non_temporal_question_is_false():
    chain = FakeChain("NO")
    result = await is_temporal_question("What's your favorite sandwich?", chain=chain)
    assert result is False


@pytest.mark.asyncio
async def test_yes_with_extra_text_is_still_true():
    chain = FakeChain("Yes, this is a Temporal question.")
    result = await is_temporal_question("How do retries work?", chain=chain)
    assert result is True


@pytest.mark.asyncio
async def test_answer_temporal_question_uses_chain_and_returns_text():
    chain = FakeDocChain("Temporal workflows guarantee that your code runs to completion.")
    question = "What guarantee does Temporal provide?"

    result = await answer_temporal_question(question, chain=chain)

    assert "Temporal workflows guarantee" in result
    assert chain.last_input == question
