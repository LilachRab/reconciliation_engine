import polars as pl

from constants import RECONCILIATION_STATUSES


def reconcile_claims(
    claims_df: pl.DataFrame, invoices_df: pl.DataFrame
) -> pl.DataFrame:
    invoice_totals = invoices_df.group_by("claim_id").agg(
        pl.col("transaction_value").sum().alias("total_transaction_value")
    )

    reconciled = (
        claims_df.join(invoice_totals, on="claim_id", how="left")
        .with_columns(pl.col("total_transaction_value").fill_null(0.0))
        .with_columns(
            pl.when(pl.col("total_transaction_value") == pl.col("benefit_amount"))
            .then(pl.lit(RECONCILIATION_STATUSES["BALANCED"]))
            .when(pl.col("total_transaction_value") > pl.col("benefit_amount"))
            .then(pl.lit(RECONCILIATION_STATUSES["OVERPAID"]))
            .otherwise(pl.lit(RECONCILIATION_STATUSES["UNDERPAID"]))
            .alias("reconciliation_status")
        )
        .select(
            [
                "claim_id",
                "patient_id",
                "charges_amount",
                "benefit_amount",
                "total_transaction_value",
                "reconciliation_status",
            ]
        )
    )

    return reconciled


def analyze_reconciliation_results(reconciliation_df: pl.DataFrame) -> dict:
    total_claims = reconciliation_df.height

    if total_claims == 0:
        return {
            "total_claims": 0,
            "balanced": {"count": 0, "percentage": 0},
            "overpaid": {"count": 0, "percentage": 0},
            "underpaid": {"count": 0, "percentage": 0},
        }

    balanced_count = reconciliation_df.filter(
        pl.col("reconciliation_status") == RECONCILIATION_STATUSES["BALANCED"]
    ).height
    overpaid_count = reconciliation_df.filter(
        pl.col("reconciliation_status") == RECONCILIATION_STATUSES["OVERPAID"]
    ).height
    underpaid_count = reconciliation_df.filter(
        pl.col("reconciliation_status") == RECONCILIATION_STATUSES["UNDERPAID"]
    ).height

    total_overpaid_amount = (
        reconciliation_df.filter(
            pl.col("reconciliation_status") == RECONCILIATION_STATUSES["OVERPAID"]
        )
        .with_columns(
            (pl.col("total_transaction_value") - pl.col("benefit_amount")).alias(
                "overpaid_amount"
            )
        )
        .select(pl.col("overpaid_amount").sum())
        .item()
        or 0.0
    )

    total_underpaid_amount = (
        reconciliation_df.filter(
            pl.col("reconciliation_status") == RECONCILIATION_STATUSES["UNDERPAID"]
        )
        .with_columns(
            (pl.col("benefit_amount") - pl.col("total_transaction_value")).alias(
                "underpaid_amount"
            )
        )
        .select(pl.col("underpaid_amount").sum())
        .item()
        or 0.0
    )

    return {
        "total_claims": total_claims,
        "balanced": {
            "count": balanced_count,
            "percentage": round((balanced_count / total_claims * 100), 2),
        },
        "overpaid": {
            "count": overpaid_count,
            "percentage": round((overpaid_count / total_claims * 100), 2),
            "amount": total_overpaid_amount,
        },
        "underpaid": {
            "count": underpaid_count,
            "percentage": round((underpaid_count / total_claims * 100), 2),
            "amount": total_underpaid_amount,
        },
        "total_overpaid_and_underpaid_claims": {
            "count": overpaid_count + underpaid_count,
            "percentage": round(
                ((overpaid_count + underpaid_count) / total_claims * 100), 2
            ),
            "amount": total_overpaid_amount + total_underpaid_amount,
        },
    }


def get_reconciliation_filters():
    return {
        "balanced_filter": pl.col("reconciliation_status")
        == RECONCILIATION_STATUSES["BALANCED"],
        "overpaid_filter": pl.col("reconciliation_status")
        == RECONCILIATION_STATUSES["OVERPAID"],
        "underpaid_filter": pl.col("reconciliation_status")
        == RECONCILIATION_STATUSES["UNDERPAID"],
    }
