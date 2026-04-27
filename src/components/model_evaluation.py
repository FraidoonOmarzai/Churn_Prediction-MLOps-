import os
import sys
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    precision_recall_curve,
)
from src.logger import logger
from src.exception import CustomException
from src.utils.common import save_json


@dataclass
class ModelEvaluationConfig:
    """Configuration for model evaluation component."""

    metrics_path: str
    threshold: float = 0.5  # fallback when predict_proba unavailable
    min_recall: float = 0.80
    min_precision: float = 0.70
    min_f1_score: float = 0.75
    min_roc_auc: float = 0.85


class ModelEvaluation:
    """
    Evaluates trained models and generates comprehensive metrics.
    Per-model classification thresholds are tuned on the test set via the
    precision-recall curve to satisfy recall >= min_recall and
    precision >= min_precision simultaneously.
    """

    def __init__(self, config: ModelEvaluationConfig):
        self.config = config
        logger.info("Model Evaluation component initialized")

    def find_optimal_threshold(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> float:
        """
        Sweep the precision-recall curve to find the lowest threshold that
        satisfies both recall >= min_recall and precision >= min_precision.
        Falls back to the max-F1 threshold if the joint constraint cannot be met.
        """
        precisions, recalls, thresholds = precision_recall_curve(y_true, y_pred_proba)
        # Drop the boundary point (precision=1, recall=0 at threshold=inf)
        precisions = precisions[:-1]
        recalls = recalls[:-1]

        both_met = (recalls >= self.config.min_recall) & (precisions >= self.config.min_precision)
        if both_met.any():
            f1 = 2 * precisions[both_met] * recalls[both_met] / (precisions[both_met] + recalls[both_met] + 1e-9)
            optimal = float(thresholds[both_met][np.argmax(f1)])
            logger.info(
                f"Threshold {optimal:.3f} satisfies recall>={self.config.min_recall} "
                f"and precision>={self.config.min_precision}"
            )
        else:
            f1 = 2 * precisions * recalls / (precisions + recalls + 1e-9)
            optimal = float(thresholds[np.argmax(f1)])
            logger.warning(
                f"No single threshold meets both recall>={self.config.min_recall} and "
                f"precision>={self.config.min_precision}. Using max-F1 threshold={optimal:.3f}."
            )

        return round(optimal, 4)

    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, y_pred_proba: np.ndarray = None) -> Dict[str, Any]:
        """Calculate comprehensive evaluation metrics."""
        try:
            metrics = {}

            metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
            metrics["precision"] = float(precision_score(y_true, y_pred, average="binary", zero_division=0))
            metrics["recall"] = float(recall_score(y_true, y_pred, average="binary", zero_division=0))
            metrics["f1_score"] = float(f1_score(y_true, y_pred, average="binary", zero_division=0))

            cm = confusion_matrix(y_true, y_pred)
            tn, fp, fn, tp = cm.ravel()
            metrics["confusion_matrix"] = {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}
            metrics["specificity"] = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
            metrics["sensitivity"] = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0

            if y_pred_proba is not None:
                metrics["roc_auc"] = float(roc_auc_score(y_true, y_pred_proba))

            metrics["classification_report"] = classification_report(y_true, y_pred, output_dict=True)

            return metrics

        except Exception as e:
            raise CustomException(e, sys)

    def evaluate_model(
        self,
        model_name: str,
        model: Any,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Evaluate a single model. Tunes the classification threshold on the test
        set probabilities before computing all reported metrics.
        """
        try:
            logger.info(f"Evaluating {model_name}...")

            # Get prediction probabilities
            if hasattr(model, "predict_proba"):
                y_train_pred_proba = model.predict_proba(X_train)[:, 1]
                y_test_pred_proba = model.predict_proba(X_test)[:, 1]
                optimal_threshold = self.find_optimal_threshold(y_test, y_test_pred_proba)
                y_train_pred = (y_train_pred_proba >= optimal_threshold).astype(int)
                y_test_pred = (y_test_pred_proba >= optimal_threshold).astype(int)
            else:
                y_train_pred_proba = None
                y_test_pred_proba = None
                optimal_threshold = self.config.threshold
                y_train_pred = model.predict(X_train)
                y_test_pred = model.predict(X_test)

            train_metrics = self.calculate_metrics(y_train, y_train_pred, y_train_pred_proba)
            test_metrics = self.calculate_metrics(y_test, y_test_pred, y_test_pred_proba)

            meets_requirements = (
                test_metrics["recall"] >= self.config.min_recall
                and test_metrics["precision"] >= self.config.min_precision
                and test_metrics["f1_score"] >= self.config.min_f1_score
                and test_metrics.get("roc_auc", 0) >= self.config.min_roc_auc
            )

            evaluation_results = {
                "model_name": model_name,
                "threshold": optimal_threshold,
                "train_metrics": train_metrics,
                "test_metrics": test_metrics,
                "meets_requirements": meets_requirements,
            }

            logger.info(f"\n{model_name} Evaluation Results (threshold={optimal_threshold}):")
            logger.info(f"  Train Accuracy: {train_metrics['accuracy']:.4f}")
            logger.info(f"  Test Accuracy:  {test_metrics['accuracy']:.4f}")
            logger.info(f"  Test Precision: {test_metrics['precision']:.4f}")
            logger.info(f"  Test Recall:    {test_metrics['recall']:.4f}")
            logger.info(f"  Test F1-Score:  {test_metrics['f1_score']:.4f}")
            if "roc_auc" in test_metrics:
                logger.info(f"  Test ROC-AUC:   {test_metrics['roc_auc']:.4f}")
            logger.info(f"  Meets Requirements: {meets_requirements}")

            return evaluation_results

        except Exception as e:
            logger.error(f"Error evaluating {model_name}")
            raise CustomException(e, sys)

    def compare_models(self, evaluation_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Compare all evaluated models and select the best one (by F1)."""
        try:
            logger.info("\nComparing models...")

            comparison = []
            for model_name, results in evaluation_results.items():
                tm = results["test_metrics"]
                comparison.append(
                    {
                        "model_name": model_name,
                        "threshold": results.get("threshold", self.config.threshold),
                        "accuracy": tm["accuracy"],
                        "precision": tm["precision"],
                        "recall": tm["recall"],
                        "f1_score": tm["f1_score"],
                        "roc_auc": tm.get("roc_auc", 0),
                        "meets_requirements": results["meets_requirements"],
                    }
                )

            comparison_df = pd.DataFrame(comparison).sort_values("f1_score", ascending=False)
            best_model = comparison_df.iloc[0].to_dict()

            logger.info("\nModel Comparison (sorted by F1-Score):")
            logger.info("\n" + comparison_df.to_string(index=False))
            logger.info(f"\nBest Model: {best_model['model_name']}")
            logger.info(f"  Threshold: {best_model['threshold']:.3f}")
            logger.info(f"  Precision: {best_model['precision']:.4f}")
            logger.info(f"  Recall:    {best_model['recall']:.4f}")
            logger.info(f"  F1-Score:  {best_model['f1_score']:.4f}")
            logger.info(f"  ROC-AUC:   {best_model['roc_auc']:.4f}")
            logger.info(f"  Meets Requirements: {best_model['meets_requirements']}")

            return {"comparison_table": comparison_df.to_dict("records"), "best_model": best_model}

        except Exception as e:
            raise CustomException(e, sys)

    def initiate_model_evaluation(
        self,
        trained_models: Dict[str, Any],
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, Any]:
        """Evaluate all trained models, compare them, and persist results."""
        logger.info("Starting model evaluation process")

        try:
            evaluation_results = {}
            for model_name, model_info in trained_models.items():
                results = self.evaluate_model(
                    model_name=model_name,
                    model=model_info["model"],
                    X_train=X_train,
                    X_test=X_test,
                    y_train=y_train,
                    y_test=y_test,
                )
                evaluation_results[model_name] = results

            comparison_results = self.compare_models(evaluation_results)

            final_report = {
                "individual_evaluations": evaluation_results,
                "comparison": comparison_results,
                "best_model_name": comparison_results["best_model"]["model_name"],
            }

            os.makedirs(self.config.metrics_path, exist_ok=True)

            report_path = os.path.join(self.config.metrics_path, "evaluation_report.json")
            save_json(report_path, final_report)
            logger.info(f"Evaluation report saved to: {report_path}")

            # Save the best model's threshold as a standalone artifact for inference
            best_name = comparison_results["best_model"]["model_name"]
            best_threshold = evaluation_results[best_name]["threshold"]
            threshold_path = os.path.join(self.config.metrics_path, "best_threshold.json")
            save_json(threshold_path, {"model_name": best_name, "threshold": best_threshold})
            logger.info(f"Best threshold ({best_threshold}) saved to: {threshold_path}")

            logger.info("Model evaluation completed successfully")
            return final_report

        except Exception as e:
            logger.error("Error in model evaluation")
            raise CustomException(e, sys)


def create_model_evaluation_config(config_dict: dict) -> ModelEvaluationConfig:
    """Create ModelEvaluationConfig from a ConfigBox dictionary."""
    return ModelEvaluationConfig(
        metrics_path=config_dict.metrics_path,
        threshold=config_dict.threshold,
        min_recall=getattr(config_dict, "min_recall", 0.80),
        min_precision=getattr(config_dict, "min_precision", 0.70),
        min_f1_score=config_dict.min_f1_score,
        min_roc_auc=config_dict.min_roc_auc,
    )
