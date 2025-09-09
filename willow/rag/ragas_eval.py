
from datasets import Dataset
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas import evaluate

def run_ragas_evaluation(data: list[dict]):
    """
    data format: [{question, answer, context}, ...]
    """
    dataset = Dataset.from_list(data)
    result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision])
    return result
