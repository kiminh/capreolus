import os
import numpy as np
import pytest
from profane import module_registry

from capreolus.benchmark import DummyBenchmark
from capreolus.searcher import Searcher, BM25, BM25Grid
from capreolus.tests.common_fixtures import tmpdir_as_cache, dummy_index


skip_searchers = {"bm25staticrob04yang19", "BM25Grid", "BM25Postprocess", "axiomatic"}
searchers = set(module_registry.get_module_names("searcher")) - skip_searchers


@pytest.mark.parametrize("searcher_name", searchers)
def test_searcher_runnable(tmpdir_as_cache, tmpdir, dummy_index, searcher_name):
    topics_fn = DummyBenchmark.topic_file
    searcher = Searcher.create(searcher_name, provide={"index": dummy_index})
    output_dir = searcher.query_from_file(topics_fn, os.path.join(searcher.get_cache_path(), DummyBenchmark.module_name))
    assert os.path.exists(os.path.join(output_dir, "done"))


def test_searcher_bm25(tmpdir_as_cache, tmpdir, dummy_index):
    searcher = BM25(provide={"index": dummy_index})
    topics_fn = DummyBenchmark.topic_file

    output_dir = searcher.query_from_file(topics_fn, os.path.join(searcher.get_cache_path(), DummyBenchmark.module_name))

    assert output_dir == os.path.join(searcher.get_cache_path(), DummyBenchmark.module_name)

    with open(os.path.join(output_dir, "searcher"), "r") as fp:
        file_contents = fp.readlines()

    assert file_contents == ["301 Q0 LA010189-0001 1 0.139500 Anserini\n", "301 Q0 LA010189-0002 2 0.097000 Anserini\n"]


def test_searcher_bm25_grid(tmpdir_as_cache, tmpdir, dummy_index):
    searcher = BM25Grid(provide={"index": dummy_index})
    bs = np.around(np.arange(0.1, 1 + 0.1, 0.1), 1)
    k1s = np.around(np.arange(0.1, 1 + 0.1, 0.1), 1)
    topics_fn = DummyBenchmark.topic_file

    output_dir = searcher.query_from_file(topics_fn, os.path.join(searcher.get_cache_path(), DummyBenchmark.module_name))
    assert output_dir == os.path.join(searcher.get_cache_path(), DummyBenchmark.module_name)

    for k1 in k1s:
        for b in bs:
            assert os.path.exists(os.path.join(output_dir, "searcher_bm25(k1={0},b={1})_default".format(k1, b)))
    assert os.path.exists(os.path.join(output_dir, "done"))
