"""简化版训练闭环骨架：Redis Stream -> Ray Serve -> MinIO.

本脚本不直接做大规模训练，而是演示：
1. 向 Redis Stream 推送训练任务；
2. 在 Ray 端消费并“伪训练”；
3. 将结果元数据写入 MinIO（可与 star_model_versions 中的 artifact_uri 对应）。
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import ray
import redis
from minio import Minio


REDIS_URL = os.getenv("MYSTAR_REDIS_URL", "redis://localhost:6379/0")
MINIO_ENDPOINT = os.getenv("MYSTAR_MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MYSTAR_MINIO_ACCESS_KEY", "mystar")
MINIO_SECRET_KEY = os.getenv("MYSTAR_MINIO_SECRET_KEY", "mystarpass")
MINIO_BUCKET = os.getenv("MYSTAR_MINIO_BUCKET", "model-artifacts")

STREAM_KEY = os.getenv("MYSTAR_TRAIN_STREAM", "mystar:trainer:jobs")


@dataclass
class TrainJob:
    job_id: str
    star_id: str
    method: str = "qlora"
    created_at: str = datetime.utcnow().isoformat()


def enqueue_job(job: TrainJob) -> None:
    client = redis.Redis.from_url(REDIS_URL)
    client.xadd(STREAM_KEY, {"payload": json.dumps(asdict(job))})
    print(f"[trainer] enqueued job={job.job_id} star={job.star_id}")


def get_minio_client() -> Minio:
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )


@ray.remote
def train_worker(job_payload: dict[str, Any]) -> str:
    """Ray 任务：这里仅模拟训练与上传模型文件。"""

    job = TrainJob(**job_payload)
    artifact_name = f"{job.star_id}_{job.job_id}.txt"
    content = f"fake-weights for star={job.star_id} job={job.job_id} method={job.method}"

    client = get_minio_client()
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
    client.put_object(
        MINIO_BUCKET,
        artifact_name,
        data=content.encode("utf-8"),
        length=len(content.encode("utf-8")),
    )
    uri = f"s3://{MINIO_BUCKET}/{artifact_name}"
    print(f"[trainer] uploaded artifact -> {uri}")
    return uri


def run(job_id: str, star_id: str) -> None:
    """本地快速测试训练闭环."""

    ray.init(ignore_reinit_error=True)

    job = TrainJob(job_id=job_id, star_id=star_id)
    enqueue_job(job)

    # 直接在本进程内分发到 Ray，真实环境中可由独立 worker 订阅 Redis Stream。
    future = train_worker.remote(asdict(job))
    uri = ray.get(future)
    print(f"[trainer] job={job_id} completed, artifact_uri={uri}")


if __name__ == "__main__":
    run("dev-job", "dev-star")
