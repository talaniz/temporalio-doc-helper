import pytest
from langchain_agent import is_temporal_question

class FakeChain:
    def __init__(self, ressponse: str):
        self._response = ressponse
        self.last_input = None

    def invoke(self, input_dict):
        # debugging
        self.last_input = input_dict
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