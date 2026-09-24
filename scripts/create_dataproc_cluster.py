"""
create_dataproc_cluster.py
==========================
Helper script to create (or delete) the Dataproc cluster defined in
conf/gcp/dataproc_cluster.yaml using the google-cloud-dataproc Python SDK.

Usage:
    # Create the cluster
    python scripts/create_dataproc_cluster.py --action create

    # Delete the cluster (saves money when not in use)
    python scripts/create_dataproc_cluster.py --action delete

    # Create in a specific region
    python scripts/create_dataproc_cluster.py --action create --region europe-west2

Prerequisites:
    pip install google-cloud-dataproc
    Set GOOGLE_APPLICATION_CREDENTIALS or run: gcloud auth application-default login
    Set GCP_PROJECT_ID environment variable (or edit the YAML directly)

What this does:
    Reads conf/gcp/dataproc_cluster.yaml and calls the Dataproc API to
    provision a managed Spark cluster identical to what's defined there.
    You can also do the same from the gcloud CLI — this script just makes it
    more reproducible and scriptable for CI/CD.
"""

import argparse
import os
import sys
import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLUSTER_YAML = os.path.join(PROJECT_ROOT, "conf", "gcp", "dataproc_cluster.yaml")


def _load_cluster_config() -> dict:
    with open(CLUSTER_YAML, "r") as f:
        return yaml.safe_load(f)


def create_cluster(region: str | None = None) -> None:
    """Create the Dataproc cluster from conf/gcp/dataproc_cluster.yaml."""
    try:
        from google.cloud import dataproc_v1
    except ImportError:
        print("  ❌  google-cloud-dataproc not installed.")
        print("     Run: pip install google-cloud-dataproc")
        sys.exit(1)

    cfg = _load_cluster_config()
    project_id = os.getenv("GCP_PROJECT_ID", cfg["project_id"])
    cluster_region = region or cfg["region"]
    cluster_name = cfg["cluster_name"]

    print(f"  Creating Dataproc cluster '{cluster_name}'...")
    print(f"  Project : {project_id}")
    print(f"  Region  : {cluster_region}")
    print()

    # Build the Dataproc Cluster proto from YAML values
    cluster = {
        "project_id": project_id,
        "cluster_name": cluster_name,
        "config": {
            "master_config": {
                "num_instances": cfg["master"]["num_instances"],
                "machine_type_uri": cfg["master"]["machine_type"],
                "disk_config": {
                    "boot_disk_type": cfg["master"]["disk"]["type"],
                    "boot_disk_size_gb": cfg["master"]["disk"]["size_gb"],
                },
            },
            "worker_config": {
                "num_instances": cfg["workers"]["num_instances"],
                "machine_type_uri": cfg["workers"]["machine_type"],
                "disk_config": {
                    "boot_disk_type": cfg["workers"]["disk"]["type"],
                    "boot_disk_size_gb": cfg["workers"]["disk"]["size_gb"],
                },
            },
            "software_config": {
                "image_version": cfg["image_version"],
                "properties": cfg["software_config"]["properties"],
                "optional_components": [
                    dataproc_v1.Component[c]
                    for c in cfg["software_config"].get("optional_components", [])
                    if hasattr(dataproc_v1.Component, c)
                ],
            },
            "lifecycle_config": {
                "idle_delete_ttl": {
                    "seconds": int(
                        cfg.get("lifecycle_config", {})
                        .get("idle_delete_ttl", "3600s")
                        .replace("s", "")
                    )
                }
            },
        },
        "labels": cfg.get("labels", {}),
    }

    client = dataproc_v1.ClusterControllerClient(
        client_options={"api_endpoint": f"{cluster_region}-dataproc.googleapis.com:443"}
    )

    operation = client.create_cluster(
        request={
            "project_id": project_id,
            "region": cluster_region,
            "cluster": cluster,
        }
    )

    print("  Waiting for cluster creation (this takes ~2–4 minutes)...")
    result = operation.result()
    print(f"  ✅  Cluster '{result.cluster_name}' created successfully!")
    print(f"      State: {dataproc_v1.ClusterStatus.State(result.status.state).name}")


def delete_cluster(region: str | None = None) -> None:
    """Delete the Dataproc cluster to stop incurring compute costs."""
    try:
        from google.cloud import dataproc_v1
    except ImportError:
        print("  ❌  google-cloud-dataproc not installed.")
        sys.exit(1)

    cfg = _load_cluster_config()
    project_id = os.getenv("GCP_PROJECT_ID", cfg["project_id"])
    cluster_region = region or cfg["region"]
    cluster_name = cfg["cluster_name"]

    print(f"  Deleting Dataproc cluster '{cluster_name}'...")
    client = dataproc_v1.ClusterControllerClient(
        client_options={"api_endpoint": f"{cluster_region}-dataproc.googleapis.com:443"}
    )

    operation = client.delete_cluster(
        request={
            "project_id": project_id,
            "region": cluster_region,
            "cluster_name": cluster_name,
        }
    )
    operation.result()
    print(f"  ✅  Cluster '{cluster_name}' deleted.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Dataproc cluster for Supply Chain Hub")
    parser.add_argument("--action", choices=["create", "delete"], required=True)
    parser.add_argument("--region", default=None, help="Override cluster region")
    args = parser.parse_args()

    print("=" * 65)
    print(f"  Dataproc Cluster Manager — Enterprise Supply Chain Hub")
    print("=" * 65)

    if args.action == "create":
        create_cluster(args.region)
    elif args.action == "delete":
        delete_cluster(args.region)


if __name__ == "__main__":
    main()
