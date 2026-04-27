import logging

from src.pipelines.train_pipeline import run_training


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_training()
