from types import SimpleNamespace
from src.llm_processor import split_into_chunks, create_script

class DummyResponses:
    def __init__(self):
        self.calls = []
    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text="Generated transcript for podcast")


def test_chunking():
    assert split_into_chunks("one two three four five", 2) == ["one two", "three four", "five"]


def test_short_source_one_call():
    fake = SimpleNamespace(responses=DummyResponses())
    assert create_script("A short real lesson", client=fake) == "Generated transcript for podcast"
    assert len(fake.responses.calls) == 1
    assert fake.responses.calls[0]["model"]


def test_long_source_map_reduce():
    fake = SimpleNamespace(responses=DummyResponses())
    create_script("lesson " * 4000, client=fake)
    assert len(fake.responses.calls) == 3  # 2 parts + final synthesis
