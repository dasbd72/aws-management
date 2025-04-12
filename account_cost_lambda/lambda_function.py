import json
from datetime import datetime, timedelta

import boto3
import pytz


def get_cost_and_usage(
    granularity="MONTHLY",
    with_resources=False,
):
    """
    Retrieves AWS billing data using the Cost Explorer service.
    """
    try:
        # Create a Cost Explorer client
        client = boto3.client("ce")

        # Define the granularity of the data (e.g., monthly, daily)
        # granularity = "MONTHLY"

        # Define the time period for the billing data
        now = datetime.now(pytz.utc)

        if granularity == "MONTHLY":
            start = now.replace(day=1)
            end = start.replace(month=now.month + 1, day=1) - timedelta(days=1)
            time_period = {
                "Start": start.strftime("%Y-%m-%d"),
                "End": end.strftime("%Y-%m-%d"),
            }

        elif granularity == "DAILY":
            start = now - timedelta(days=7)
            end = start + timedelta(days=7)
            time_period = {
                "Start": start.strftime("%Y-%m-%d"),
                "End": end.strftime("%Y-%m-%d"),
            }

        # Define the metrics to retrieve (e.g., UnblendedCost, BlendedCost)
        metrics = [
            "UnblendedCost",
        ]

        # Define the dimensions to group by (e.g., RESOURCE_ID)
        group_by = [
            {
                "Type": "DIMENSION",
                "Key": "SERVICE",
            },
        ]

        # Get cost and usage data
        if not with_resources:
            response = client.get_cost_and_usage(
                Granularity=granularity,
                TimePeriod=time_period,
                Metrics=metrics,
            )

        else:
            response = client.get_cost_and_usage(
                Granularity=granularity,
                TimePeriod=time_period,
                Metrics=metrics,
                GroupBy=group_by,
            )

        # Extract the billing data
        cost_data = []
        for result in response["ResultsByTime"]:
            cost_info = {
                "Start": result["TimePeriod"]["Start"],
                "End": result["TimePeriod"]["End"],
                "UnblendedCost": result["Total"]["UnblendedCost"]["Amount"],
                "Unit": result["Total"]["UnblendedCost"]["Unit"],
            }
            cost_data.append(cost_info)

        return cost_data

    except Exception as e:
        print(f"Error retrieving billing data: {e}")
        return None


def lambda_handler(event, context):
    cost_data = get_cost_and_usage()

    if cost_data:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"cost_data": cost_data}),
        }
    else:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Failed to retrieve cost data"}),
        }
