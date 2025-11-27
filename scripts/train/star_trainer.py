"""占位脚本：后续扩展 RL 训练流程."""

def run(job_id: str) -> None:
    print(f"[MyriadStar::Trainer] job={job_id} -> queued")


if __name__ == "__main__":
    run("dev-job")
