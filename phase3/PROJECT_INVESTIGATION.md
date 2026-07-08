# Điều tra dự án Phase 3 — cần làm gì & kiến trúc tối ưu

Tài liệu này là kết quả **đọc trực tiếp code + config** (không chỉ đọc doc): `techx-corp-chart/values.yaml`, `flagd/demo.flagd.json`, `deploy/*`, `src/llm`, `src/product-reviews`, `pb/demo.proto`, `build-push-images.sh`. Mục tiêu: nêu rõ **(A) dự án này là gì**, **(B) phải làm gì để chạy được**, **(C) hiện trạng yếu ở đâu**, **(D) kiến trúc tối ưu nên hướng tới**.

---

## A. Dự án này thực chất là gì

Đây là **OpenTelemetry Astronomy Shop demo** được **rebrand thành "TechX Corp"** — một storefront TMĐT microservice polyglot, thêm một tầng AI (`llm` + `product-reviews`) và biến flagd thành **cỗ máy bơm sự cố do BTC điều khiển từ xa**.

- **~18 service** (Go, Python, .NET, Java, Rust, PHP, C++, Ruby, Node, Kotlin, TS) nói chuyện qua **gRPC**, một **Kafka** cho luồng async, cổng vào duy nhất **frontend-proxy (Envoy) :8080**.
- **Tầng AI hiện tại là MOCK:** `src/llm/app.py` là một Flask server giả lập OpenAI API — nó **không gọi model thật**, chỉ trả về summary pre-generated từ `product-review-summaries.json`, và **cố tình trả sai** khi cờ `llmInaccurateResponse` bật cho product `L9ECAV7KIM`. Nhóm AIO phải cắm model thật (`values-aio-llm.yaml`).
- **Sự cố được bơm qua 16 feature flag** (xem §C.6). Service đọc flag qua OpenFeature/flagd. **Đây là hạ tầng cấm đụng** — gỡ = disqualify.

> Kết luận: "làm dự án này" **không phải** viết app từ đầu. Là **tiếp quản một hệ thống có sẵn đầy nợ kỹ thuật**, làm nó cứng cáp/rẻ/an toàn/quan sát được, và (với AIO) nâng cấp tầng AI từ mock → thật + dựng trợ lý agentic.

---

## B. Phải làm gì để đưa dự án lên chạy (đường tối thiểu)

### B0. Chuẩn bị (mỗi TF, 1 lần)
- Cluster **EKS** + `kubectl` trỏ đúng; `docker buildx`+QEMU, `helm v3`, `aws` CLI đã login.
- Quyền tạo **ECR repo** trong account TF.

### B1. Build image từ source → ECR (đường A, được chấm)
```sh
REG=<ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/techx-corp
aws ecr create-repository --repository-name techx-corp --region <REGION>
aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com
# sửa techx-corp-platform/.env.override:  IMAGE_NAME=$REG   (giữ IMAGE_VERSION=1.0)
./deploy/build-push-images.sh     # smoke build checkout → multi-arch build+push 17 app image
```
> `build-push-images.sh` gọi `make build-multiplatform-and-push`. Chỉ **app image** vào ECR; flagd/postgres/collector/grafana/opensearch/valkey/kafka pull từ registry public.

### B2. Chuẩn bị & deploy chart
```sh
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo add opensearch https://opensearch-project.github.io/helm-charts
helm dependency build ./techx-corp-chart

NS=techx-<tf>
helm upgrade --install techx-corp ./techx-corp-chart -n $NS --create-namespace \
  --set default.image.repository=$REG \
  -f deploy/values-observability.yaml \
  -f deploy/values-flagd-sync.yaml            # BẮT BUỘC: cắm nguồn flag trung tâm (cần <TOKEN> BTC cấp)
```
- **Mỗi lần `helm upgrade` phải ghép lại `-f values-flagd-sync.yaml`**, nếu không flagd rớt về local → bị coi như đổi hướng cơ chế sự cố (disqualify).
- **AIO:** tạo secret `llm-api-key` rồi ghép thêm `-f deploy/values-aio-llm.yaml` để cắm LLM thật.

### B3. Verify hệ sống
```sh
kubectl -n $NS get pods                            # tất cả Running/Ready
kubectl -n $NS port-forward svc/frontend-proxy 8080:8080
# :8080 storefront · mở 1 sản phẩm → có tóm tắt AI · /grafana /jaeger/ui /loadgen
```

### B4. Sau khi baseline chạy (đây mới là phần được chấm)
1. Tự đánh giá hệ thống → dựng **backlog ưu tiên** (rủi ro × business).
2. Dựng **dashboard SLO** (không đo được thì không quản được).
3. Bật **AWS Budgets + Cost Anomaly Detection** (~$300/tuần/TF).
4. Chuẩn bị **Pitch** cuối Tuần 1.

---

## C. Hiện trạng — hệ thống yếu ở đâu (đọc thẳng từ config)

Đây là những điểm **thấy rõ trong `values.yaml`** — chính là "nợ kỹ thuật" sinh viên phải nhìn ra. Chia theo 5 trụ.

### C.1 Reliability — yếu nhất, đúng như INCIDENT_HISTORY
- **`default.replicas: 1` — MỌI service single-replica → SPOF toàn hệ.** Bất kỳ pod nào chết/reschedule là mất luồng. (khớp INC-2 mất giỏ, INC-3 lỗi deploy.)
- **Không có `readinessProbe`/`livenessProbe` nào được định nghĩa** cho app component → traffic vào pod chưa sẵn sàng (khớp INC-3), pod treo không bị restart.
- **Stateful đều ephemeral, không bền, không HA:**
  - `postgresql` replicas:1, không PVC → **mất data khi reschedule**.
  - `valkey-cart` replicas:1, không persistence → **mất giỏ hàng** (khớp INC-2).
  - `kafka` replicas:1 (single broker, `KAFKA_HEAP_OPTS -Xmx400M`) → SPOF hàng đợi đơn hàng.
  - `opensearch` singleNode + `persistence.enabled:false`; `prometheus` `persistentVolume:false` retention 7d; `jaeger` storage **memory** (max 25k traces) → mất telemetry khi restart.
- **Không có PodDisruptionBudget, không topologySpreadConstraints, không anti-affinity.**
- **Checkout `resources.limits.memory: 20Mi` + `GOMEMLIMIT 16MiB`** — cực sát, dễ OOM dưới tải (liên quan INC-1 connection pool cạn khi tải tăng).

### C.2 Performance Efficiency
- **Không có CPU limits/requests ở đâu cả** — chỉ có memory limits. Không có `requests` → scheduler đặt pod mù, QoS = BestEffort/Burstable lẫn lộn, dễ bị evict.
- **Không có HPA/autoscaling** — flag `loadGeneratorFloodHomepage` và `adHighCpu` sẽ đập thẳng vào service không co giãn.
- **Collector chạy `mode: daemonset`** — 1 pod/node, chi phí tăng theo số node.
- `recommendation` limit 500Mi "to enable recommendationCache" — cache tốn RAM, cần cân với cost.

### C.3 Security — nhiều lỗ hổng cấu hình (sửa tận gốc, không phải sự cố bơm)
- **Mật khẩu hardcode trong values.yaml:** postgres `root/otel` và `otelu/otelp`; `DB_CONNECTION_STRING` để lộ credential trong env plaintext.
- **`sslmode=disable`** cho postgres; **Kafka PLAINTEXT** không TLS/auth.
- **Grafana:** `auth.anonymous.enabled + org_role: Admin` và `disable_login_form: true`, `adminPassword: admin` → ai vào cũng là admin.
- **OpenSearch `DISABLE_SECURITY_PLUGIN: true`** → không auth.
- **flagd-ui `SECRET_KEY_BASE` hardcode** trong values.
- **Nhiều service thiếu `securityContext`** (chỉ frontend/frontend-proxy/payment/quote/kafka/valkey set `runAsNonRoot`); phần lớn **chạy root**, không `readOnlyRootFilesystem`, không drop capabilities.
- **Không có NetworkPolicy** — mọi pod gọi được mọi pod.
- Secret quản lý bằng plaintext env, chưa dùng External Secrets/SSM/Secrets Manager.

### C.4 Cost Optimization
- Không có `requests` → không bin-pack được → lãng phí node.
- Không spot, không Karpenter/Cluster Autoscaler → node tĩnh luôn bật.
- Observability nặng: opensearch 1100Mi + jaeger 600Mi + prometheus 400Mi + collector daemonset. Retention/replica chưa cân với ngân sách ~$300/tuần.
- In-cluster DB dùng EBS gp2 mặc định; nếu lên managed (RDS/MSK/ElastiCache) phải cân Multi-AZ vs cost.

### C.5 Auditability
- **Chưa có** K8s audit policy, CloudTrail wiring, hay change management trong repo.
- Deploy bằng `helm upgrade` tay, không GitOps → khó truy "ai đổi gì khi nào".
- Grafana anonymous admin = không truy được hành động người dùng.
- **Chưa có ADR/decision-log/postmortem template** trong repo (deliverable bắt buộc).

### C.6 Tầng AI (cho AIO)
- **`llm` là MOCK** (Flask, trả summary tĩnh). Phải cắm model thật qua `values-aio-llm.yaml` + secret.
- **Không có eval, không guardrail, không fallback** cho tóm tắt. Cờ `llmInaccurateResponse` chứng minh: hệ thống **sẵn sàng show tóm tắt sai** cho product `L9ECAV7KIM` mà không ai chặn.
- **Fallback hiện tại quá thô:** khi `llmRateLimitError` (429 ~50%), `product-reviews` chỉ trả chuỗi "The system is unable to process your response" — chưa retry/backoff/cache.
- **Chưa có "Shopping Copilot" agentic** — BTC không phát code. Nhưng proto **đã có sẵn mọi RPC làm tool:** `ProductCatalogService.SearchProducts/GetProduct/ListProducts`, `ProductReviewService.GetProductReviews/AskProductAIAssistant`, `CartService.AddItem/GetCart/EmptyCart`, `RecommendationService`, `CurrencyService`, `ShippingService.GetQuote`. AIO tự wire agent gọi các RPC này + guardrail (allow-list, confirmation trước AddItem, cấm EmptyCart/checkout tự động).

### C.7 Bản đồ 16 flag sự cố → trụ chịu trách nhiệm (làm hệ thống *chịu được*, KHÔNG tắt flag)

| Flag | Triệu chứng | Trụ / hướng xử lý |
|---|---|---|
| `llmInaccurateResponse` | tóm tắt sai cho L9ECAV7KIM | AIE: faithfulness eval + guardrail chặn output sai |
| `llmRateLimitError` | llm 429 ~50% | AIE: retry/backoff + cache + fallback graceful |
| `paymentFailure` (10–100%), `paymentUnreachable` | charge lỗi | Reliability: **checkout critical path** — retry, circuit breaker, idempotency |
| `cartFailure`, `failedReadinessProbe` | cart lỗi / probe fail | Reliability: multi-replica + probe đúng + fallback |
| `kafkaQueueProblems` | consumer lag spike | Reliability/Perf: scale consumer, DLQ, backpressure |
| `productCatalogFailure` | catalog lỗi 1 product | Reliability: retry/timeout/circuit break ở caller |
| `recommendationCacheFailure` | cache rec lỗi | Reliability/Perf: degrade gracefully |
| `adManualGc`, `adHighCpu`, `adFailure` | ad ngốn CPU/GC/chết | Perf: CPU limit, timeout, degrade (ad không được kéo trang chết) |
| `loadGeneratorFloodHomepage` | flood homepage | Perf: HPA, rate limit, load shedding |
| `imageSlowLoad` | ảnh chậm 5–10s | Perf: timeout, lazy load, CDN |
| `emailMemoryLeak` | email leak RAM | Reliability: memory limit + restart policy, OOM containment |

---

## D. Kiến trúc tối ưu nên hướng tới

Không phải "làm hết mọi thứ" — Phase 3 chấm **judgment + đánh đổi trong ngân sách**. Dưới đây là target hợp lý theo trụ, kèm mức ưu tiên.

### D.1 Reliability (ưu tiên #1 — checkout là luồng ra tiền)
- **Checkout path HA trước tiên:** `checkout`, `cart`, `payment`, `product-catalog`, `frontend`, `frontend-proxy` → **≥2 replica** + **readiness/liveness probe** + **PodDisruptionBudget** + **topologySpreadConstraints** (spread qua AZ/node).
- **Resilience patterns ở caller:** timeout hợp lý, retry có jitter, **circuit breaker**, idempotency key cho payment. Có thể cân nhắc service mesh nhẹ (Linkerd) hoặc làm ở tầng code — cân với cost/complexity.
- **State bền:**
  - `valkey-cart` → bật persistence (AOF) hoặc **ElastiCache** (cân Multi-AZ vs cost) để hết mất giỏ.
  - `postgresql` → PVC + backup, hoặc **RDS** (directive có thể ép); Multi-AZ chỉ khi ROI đáng.
  - `kafka` → tăng replication/partition hoặc **MSK**; consumer có DLQ + backpressure.
- **Connection pool** (checkout/catalog) right-size + alert khi gần cạn (đóng INC-1).
- **Nâng `checkout` memory limit** khỏi 20Mi để hết OOM dưới tải; đặt `requests`.

### D.2 Performance Efficiency
- **Đặt `requests` + `limits` (CPU & memory) cho mọi service** → QoS Guaranteed cho critical path, bin-pack tốt.
- **HPA** cho frontend/frontend-proxy/product-catalog/recommendation (theo CPU + custom metric từ Prometheus). Trị `loadGeneratorFloodHomepage`.
- **Cluster autoscaler / Karpenter** để co giãn node theo tải.
- **Load shedding / rate limit ở Envoy** (frontend-proxy) chống flood.
- Cân `recommendation` cache RAM vs hit-rate.

### D.3 Cost Optimization (trần ~$300/tuần)
- **Right-size bằng số thật** từ Prometheus (VPA recommend), không đoán.
- **Spot/Karpenter** cho workload stateless; on-demand cho stateful.
- **Observability tiering:** giảm retention Prometheus/OpenSearch hợp lý; sampling trace ở collector (hiện chưa có tail-sampling) để cắt chi phí Jaeger/storage.
- **Managed vs self-host:** chỉ lên RDS/MSK/ElastiCache khi reliability ROI vượt chi phí; ghi ADR. Single-AZ mặc định, Multi-AZ chỉ cho store trọng yếu.
- Bật **AWS Budgets + Cost Anomaly Detection** ngay tuần 1.

### D.4 Security (hardening tận gốc — đây là lỗ cấu hình, không phải sự cố bơm)
- **Bỏ mọi secret hardcode** → Kubernetes Secret + **External Secrets Operator / AWS Secrets Manager / SSM**; bật IRSA cho pod.
- **Bật TLS + auth:** postgres `sslmode=require`, Kafka SASL/TLS, OpenSearch bật security plugin, Grafana tắt anonymous admin + đổi password.
- **Pod hardening chuẩn:** `runAsNonRoot`, `readOnlyRootFilesystem`, `drop ALL capabilities`, seccomp `RuntimeDefault` cho mọi service (nhiều cái đang chạy root).
- **NetworkPolicy** least-privilege: chỉ cho luồng gRPC hợp lệ (vd chỉ checkout gọi payment).
- Image scanning (Trivy) trong CI; pin digest thay tag `1.0`.

### D.5 Auditability (xuyên suốt)
- **GitOps (ArgoCD/Flux)** thay `helm upgrade` tay → mọi thay đổi có commit ký tên, truy được.
- **EKS control-plane audit log → CloudWatch**; **CloudTrail** cho AWS API.
- **Log integrity:** OpenSearch có auth + retention; k8s audit policy.
- Repo có sẵn **ADR template + decision log + postmortem/COE template** (deliverable bắt buộc).

### D.6 Tầng AI (AIO)
- **Phần A — nâng chất tóm tắt:** cắm LLM thật → **faithfulness eval** (tóm tắt khớp review, chặn L9ECAV7KIM sai) đưa vào CI → **guardrail** (prompt-injection trong review, PII, lộ system prompt) → **fallback + cache + retry/backoff** cho 429 → tối ưu token/route model rẻ.
- **Phần B — Shopping Copilot agentic:** wire agent (framework tool-calling tùy chọn) vào các RPC sẵn có; **3 intent core** (NL search / RAG grounded / cart có confirmation). Bắt buộc: **tool allow-list, confirmation gate trước mọi hành động ghi (AddItem), cấm EmptyCart/checkout tự động (excessive-agency), loop guard, audit log mọi tool call, multi-turn context, fallback**. Có **eval task-success** tái tạo được.
- **AIOps:** anomaly detection đa tín hiệu trên Prometheus/Jaeger/OpenSearch + vòng phát hiện→dry-run→xử lý→verify→rollback, **chạy liên tục** trong lúc vận hành.

---

## E. Thứ tự thực thi khuyến nghị (2-3 tuần)

| Ưu tiên | Việc | Trụ | Lý do |
|---|---|---|---|
| P0 | Baseline chạy + dashboard SLO + AWS Budgets | Ops | không đo/không thấy thì không quản được |
| P0 | Probes + ≥2 replica cho checkout path + PDB | Reliability | luồng ra tiền, SPOF hiện tại, rẻ |
| P1 | requests/limits CPU+mem toàn hệ + HPA critical | Perf/Cost | ổn định scheduling, trị flood, tiết kiệm node |
| P1 | valkey/postgres bền (persistence/managed) | Reliability | đóng INC-2, chống mất data |
| P1 | Bỏ secret hardcode + pod hardening + NetworkPolicy | Security | lỗ hổng rõ ràng, sửa gốc |
| P1 | (AIO) eval + guardrail + fallback cho tóm tắt | AIE | chống show tóm tắt sai, nền cho phần B |
| P2 | Circuit breaker/retry ở checkout→payment | Reliability | chịu paymentFailure/Unreachable |
| P2 | (AIO) Shopping Copilot agentic + eval task-success | AIE | phần tạo khác biệt, đua top |
| P2 | (AIO) AIOps loop chạy liên tục | AIOps | bar để được chấm cao |
| P2 | GitOps + audit logging + ADR templates | Auditability | truy vết, deliverable |
| P3 | Spot/Karpenter, trace sampling, retention tuning | Cost | tối ưu sau khi đã ổn định |

> Nguyên tắc xuyên suốt: **mỗi thay đổi có đo before/after, có ADR ký tên, không phá SLO/ngân sách, KHÔNG đụng đường dây flagd/incident.** Sự cố bơm vào thì làm hệ thống *chịu được* (fallback/retry/containment), lỗ hổng cấu hình thì *sửa tận gốc*.
