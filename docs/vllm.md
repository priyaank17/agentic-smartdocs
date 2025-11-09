# vLLM Deployment

- GPU pool: `Standard_NC6` or `Standard_ND96` with autoscaling.
- Image: build from `src/deployments/docker/Dockerfile.vllm` and push to ACR.
- Deployment manifest: `src/deployments/aks/vllm-deployment.yaml` requests a single GPU and exposes port 9000 for /completions + /vision/completions.
- Throughput tuning: configure tensor parallel size via `PALIGEMMA_TP_SIZE`, enable batching in vLLM via `--max-num-batched-tokens` (set in CMD if you extend the Dockerfile).
- Caching: mount Azure Files as `/models` to persist Paligemma weights and LoRA adapters across pod restarts.
- Cost optimization: use cluster autoscaler + HPA on GPU deployment, and KEDA if queue-driven workloads are preferred.
