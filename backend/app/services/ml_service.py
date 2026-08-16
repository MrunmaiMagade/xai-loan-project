"""
Bridges the Flask backend to the ml/ package (prediction, SHAP, LIME,
counterfactuals, fairness). This is the ONLY place that touches the ml/
package directly -- routes call this service, never ml/ modules directly
(spec section 34: routes -> services -> ML/DB, not all-in-one routes).
"""

import os
import sys
from functools import lru_cache

import pandas as pd

_ML_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml"))
if _ML_ROOT not in sys.path:
    sys.path.insert(0, _ML_ROOT)

from prediction.predictor import predict as ml_predict, load_pipeline, load_metadata, ModelNotTrainedError  # noqa: E402
from explainability.shap_explainer import local_shap_explanation, global_shap_importance  # noqa: E402
from explainability.lime_explainer import local_lime_explanation  # noqa: E402
from explainability.explanation_engine import generate_summary  # noqa: E402
from explainability.comparison import compare_explanations  # noqa: E402
from counterfactual.dice_explainer import generate_counterfactual  # noqa: E402
from fairness.fairness_analyzer import run_fairness_analysis  # noqa: E402
from config import RAW_DATA_FILE  # noqa: E402
from app.services.indian_feature_mapper import model_value_to_indian_display  # noqa: E402


class MLServiceError(Exception):
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@lru_cache(maxsize=1)
def _reference_data() -> pd.DataFrame:
    """A cached sample of real training data used as SHAP/LIME/DiCE background."""
    if not os.path.exists(RAW_DATA_FILE):
        raise MLServiceError(
            "Reference dataset not found. Run `python data/download_dataset.py` "
            "inside ml/ (requires internet) before using explainability features."
        )
    return pd.read_csv(RAW_DATA_FILE)


def _applicant_df(applicant: dict) -> pd.DataFrame:
    from prediction.predictor import applicant_to_dataframe
    return applicant_to_dataframe(applicant)


def predict_application(applicant: dict) -> dict:
    try:
        return ml_predict(applicant)
    except ModelNotTrainedError as e:
        raise MLServiceError(str(e), 503)


def get_shap_explanation(applicant: dict, prediction: str, probability: float) -> dict:
    try:
        pipeline = load_pipeline()
        contributions = local_shap_explanation(pipeline, _applicant_df(applicant), _reference_data())
        summary = generate_summary([{**item, "value": model_value_to_indian_display(item["feature"], item["value"])} for item in contributions], prediction, probability)
        return {"contributions": contributions, "plain_english": summary}
    except ModelNotTrainedError as e:
        raise MLServiceError(str(e), 503)


def get_lime_explanation(applicant: dict, prediction: str, probability: float) -> dict:
    try:
        pipeline = load_pipeline()
        contributions = local_lime_explanation(pipeline, _applicant_df(applicant), _reference_data())
        summary = generate_summary([{**item, "value": model_value_to_indian_display(item["feature"], item["value"])} for item in contributions], prediction, probability)
        return {"contributions": contributions, "plain_english": summary}
    except ModelNotTrainedError as e:
        raise MLServiceError(str(e), 503)


def get_shap_lime_comparison(shap_contributions: list, lime_contributions: list) -> dict:
    return compare_explanations(shap_contributions, lime_contributions)


def get_counterfactual(applicant: dict) -> dict:
    try:
        pipeline = load_pipeline()
        return generate_counterfactual(pipeline, _applicant_df(applicant), _reference_data())
    except ModelNotTrainedError as e:
        raise MLServiceError(str(e), 503)


def get_global_shap() -> list:
    try:
        pipeline = load_pipeline()
        return global_shap_importance(pipeline, _reference_data())
    except ModelNotTrainedError as e:
        raise MLServiceError(str(e), 503)


def get_model_metadata() -> dict:
    try:
        return load_metadata()
    except ModelNotTrainedError as e:
        raise MLServiceError(str(e), 503)


def get_fairness_report() -> dict:
    try:
        return run_fairness_analysis()
    except FileNotFoundError as e:
        raise MLServiceError(str(e), 503)
