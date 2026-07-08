# Mentor Grading Guide — Phase 3 (TechX Corp Service Takeover)

Tài liệu này liệt kê **những kiến thức một mentor cần nắm** để kèm cặp và **chấm điểm** Phase 3 cho sinh viên. Phase 3 mô phỏng việc "tiếp quản một sản phẩm AI đang chạy production": sinh viên tự đánh giá, tự ưu tiên, vận hành, xử lý sự cố và **bảo vệ quyết định** của mình. Vì thế mentor không chỉ chấm code — mà chấm **judgment, vận hành, đánh đổi business, và giao tiếp**.

> Nguồn: `README.md`, `RULES.md`, `GETTING_STARTED.md`, `onboarding/*`, `mandates/README.md`. Đọc kỹ các file này trước khi kèm nhóm.

---

## 0. Bản đồ nhanh: mentor cần biết gì

| Nhóm kiến thức | Vì sao cần | Mục |
|---|---|---|
| Format & luật chơi Phase 3 | Biết chấm cái gì, khi nào, và điều gì làm sinh viên bị loại | §1, §11 |
| Kiến trúc hệ thống (18 microservice, gRPC, Kafka, DB) | Đánh giá đề xuất kỹ thuật đúng/sai, phát hiện SPOF | §2 |
| 5 trụ CDO + Operational Excellence | Chấm nhóm CDO theo từng trụ | §3 |
| Trụ AI (AIOps + AIE) | Chấm nhóm AIO | §4 |
| SLO / Error budget | Xác minh "giữ SLO", đánh giá đánh đổi rủi ro | §5 |
| Ngân sách & Cost | Xác minh không vượt trần, đánh giá hiệu quả chi phí | §6 |
| Cơ chế sự cố (flagd/OpenFeature) | Hiểu sự cố được bơm thế nào + luật disqualify | §7 |
| Build → ECR → EKS → Helm | Xác minh hệ thống "chạy thật, không mockup" | §8 |
| Observability tooling | Tự đọc telemetry để kiểm chứng lời khai của sinh viên | §9 |
| Kiến thức AI/LLM (eval, guardrail, RAG, agentic) | Chấm chiều sâu nhóm AIO | §10 |
| Deliverables & rubric chấm | Biết chấm theo tiêu chí nào | §11, §12 |
| Kỹ năng đóng vai hội đồng phản biện | Vai chính của mentor ở Pitch & Health Readout | §13 |

---

## 1. Format, cấu trúc & timeline Phase 3

Mentor phải nắm rõ khung để biết chấm cái gì ở mốc nào.

- **Ba tầng tổ chức:** 4 Task Force (TF) vận hành/thi đấu · 13 nhóm (9 CDO + 4 AIO), mỗi nhóm 1 mentor kèm · Ban tổ chức tổng hợp & quyết định.
- **Cấu tạo TF:** mỗi TF = 1 nhóm AIO + 2–3 nhóm CDO, cùng vận hành **1 service trên 1 account riêng**.
- **Hai luồng chạy song song trong mỗi TF:**
  - **Operate** — giữ đèn sáng: on-call, incident, SLO, fix điểm yếu.
  - **Build** — ship cải tiến/feature mới; **không có checklist phát sẵn**, sinh viên tự đánh giá → đề xuất backlog.
- **Timeline 3 tuần:**
  - **Tuần 1** — Tiếp quản: build từ source → deploy chạy trên EKS (đã tính điểm) → tự đánh giá → dựng backlog ưu tiên → **Pitch bảo vệ ưu tiên** (mốc tư duy quan trọng nhất).
  - **Tuần 2–3** — Vận hành & cải tiến dưới ràng buộc: 3 nguồn việc chạy song song — (a) backlog tự chọn, (b) **directive bắt buộc** từ BTC (thả vào `mandates/`), (c) **sự cố** do BTC bơm vào.
  - **Kết thúc** — **Service Health Readout**: trình bày đã làm gì, đánh đổi gì, trạng thái service; hội đồng phản biện, có thể hỏi thẳng cá nhân.
- **Nhịp vận hành để mentor theo sát:** Standup mỗi ngày (bàn giao ca on-call) · Weekly Ops Review · sự cố ập đến bất kỳ lúc nào.

**Cross-functional là tiêu chí được chấm:** CDO lo platform/hạ tầng, AIO lo tầng AI — nhưng phải phối hợp giữ một service khỏe. Mentor quan sát sự phối hợp này.

---

## 2. Kiến trúc hệ thống — phải hiểu để đánh giá kỹ thuật

Storefront TMĐT, **microservice polyglot** trên Kubernetes, ~18 service giao tiếp chủ yếu qua **gRPC**, hàng đợi **Kafka** cho luồng bất đồng bộ. Cổng vào duy nhất: **frontend-proxy (Envoy) :8080**.

**Service mentor nên nhớ (những cái hay bị đụng khi chấm):**

| Service | Vai trò | Ngôn ngữ | Ghi chú chấm |
|---|---|---|---|
| `frontend-proxy` | Envoy, cổng vào :8080 | Envoy | route tới frontend + observability UI |
| `frontend` | Storefront web | TS/Next.js | |
| `product-catalog` | list/get/**search** | Go | postgresql |
| `product-reviews` | Review + **tóm tắt AI** + hỏi-đáp | Python | **bề mặt AI trọng tâm** |
| `llm` | Backend model | Python | **mock mặc định**, cắm model thật qua values-aio-llm |
| `cart` | Giỏ hàng | .NET/C# | valkey-cart — **từng là SPOF (INC-2)** |
| `checkout` | Điều phối đặt hàng | Go | **luồng ra tiền, quan trọng nhất** |
| `payment`, `shipping`, `quote`, `currency`, `email` | phụ trợ checkout | Node/Rust/PHP/C++/Ruby | |
| `accounting`, `fraud-detection` | consumer Kafka | .NET/Kotlin | luồng bất đồng bộ sau đặt hàng |
| `flagd` | Feature flags | flagd | **hạ tầng bơm sự cố — được bảo vệ, xem §7** |

**Data stores:** `postgresql` (catalog, reviews, accounting) · `valkey-cart` (cart) · `kafka` (checkout→accounting/fraud). Baseline là **in-cluster** (pod) — migrate sang managed (RDS/ElastiCache/MSK) là cải tiến có thể bị directive yêu cầu.

**Luồng chính cần hiểu để trace/đánh giá:**
- Duyệt sản phẩm → frontend → catalog + recommendation + ad.
- Trang sản phẩm → product-reviews → postgres **và** llm (tóm tắt AI).
- Checkout → gom cart + catalog + currency + shipping/quote + payment + email → **publish Kafka** → accounting/fraud consume.

**Điểm yếu có sẵn trong hệ thống** (mentor nên biết trước để đánh giá backlog của sinh viên có "nhìn ra" hay không): replicas/probes chưa tối ưu, SPOF ở cart, connection pool DB, thiếu readiness gating khi deploy (xem §5 Incident History).

---

## 3. Năm trụ CDO + Operational Excellence

Mentor kèm nhóm CDO phải chấm được theo trụ. Mỗi nhóm sở hữu **home-pillar** nhưng khi on-call thì xử lý mọi trụ ập tới.

1. **Security** — hardening, least-privilege, phát hiện & chặn xâm nhập, bảo vệ dữ liệu/danh tính.
2. **Reliability** — chịu lỗi, tự phục hồi, giữ SLO qua sự cố (fallback, retry, containment, replica, probe, rollback).
3. **Performance Efficiency** — đúng tài nguyên cho đúng tải: chịu tải, autoscale, multi-tenant, tối ưu độ trễ.
4. **Cost Optimization** — right-size, spot, cắt lãng phí **trong khi giữ SLA**; hiệu quả chi phí / đơn vị tải.
5. **Auditability** — truy được ai làm gì khi nào: K8s audit, CloudTrail, change management, log integrity. (Trụ xuyên suốt mọi thay đổi, linh hoạt/luân phiên.)

**Operational Excellence** — xương sống xuyên suốt cả 5 trụ: vận hành hướng tới kết quả kinh doanh (on-call, ADR, Ops Review, quy mọi quyết định về khách & doanh thu). Cả TF cùng thực hành.

**Cách phân trụ trong TF** (mentor cần biết để chấm đúng phạm vi từng nhóm):
- *TF 2 nhóm CDO:* Nhóm A (winner Phase 2) chọn 2 trụ core; Nhóm B lấy 2 trụ còn lại; cả hai luân phiên Auditability.
- *TF 3 nhóm CDO:* 2+2+1 — Nhóm C đào sâu Auditability.
- **Draft:** snake draft trên 4 trụ core (Security, Reliability, Performance, Cost) theo hạng Phase 2.

Mentor cần biết mỗi nhóm mình kèm **sở hữu trụ nào** để chấm chiều sâu đúng chỗ, đồng thời chấm khả năng xử lý trụ khác khi on-call.

---

## 4. Trụ AI — cho nhóm AIO (nằm ngoài 5 trụ CDO)

Hai hướng, mỗi hướng có phần **cốt lõi** (bắt buộc) và **mở rộng** (đua top). AIO tự đánh giá tầng AI rồi đề xuất tập trung.

### 4.1 AIOps — dùng AI để vận hành hệ thống
- **Cốt lõi:** phát hiện bất thường đa tín hiệu (latency, error rate, saturation, queue lag, cost…) + **vòng tự động hoá xử lý sự cố**: phát hiện → kiểm tra an toàn (dry-run/blast-radius) → xử lý → verify qua telemetry → rollback/escalate. **Chạy liên tục** trong lúc vận hành.
- **Mở rộng:** RCA cross-service, dự báo capacity/cost, phát hiện drift.
- **Bar chấm cao:** hệ AIOps chạy liên tục và **xử lý được sự cố thật**, không phải demo một lần.

### 4.2 AIE — làm AI trong sản phẩm
Bề mặt AI hiện tại = **tóm tắt review** (`product-reviews` + `llm`). Hai phần:

- **Phần A — nâng chất tính năng có sẵn (tóm tắt review):**
  - *Đúng đắn:* eval độ trung thực (tóm tắt khớp review gốc), **fallback** khi llm lỗi/chậm → **không bao giờ show tóm tắt sai lệch**.
  - *An toàn:* guardrail chặn prompt-injection trong review, lọc PII, chặn lộ system prompt.
  - *Chi phí/độ trễ:* cache theo sản phẩm, route model rẻ, giảm token, timeout/retry.
- **Phần B — tự dựng "Shopping Copilot" agentic** (BTC KHÔNG phát code agent):
  - **3 intent cốt lõi:** (1) tìm sản phẩm bằng ngôn ngữ tự nhiên (search catalog); (2) hỏi-đáp **grounded/RAG** từ review thật, biết nói "không có thông tin"; (3) thao tác giỏ **có xác nhận trước khi ghi, không tự checkout/xoá giỏ**.
  - **Mở rộng:** so sánh sản phẩm, cross-sell, giá/ship/quy đổi tiền.
  - **Yêu cầu xuyên suốt:** multi-turn (nhớ ngữ cảnh), tool allow-list + confirmation gate (guardrail **excessive-agency**), grounded không hallucinate, không lộ PII/system prompt, fallback + giới hạn vòng lặp + **audit log mọi lời gọi tool**.

**Nguyên tắc chấm tầng AI (5 chiều):** Ưu tiên & judgment · Engineering & Ops · Business trade-off · Năng lực AI · Communication. Được nhìn cụ thể: **chạy thật không mockup, có eval tái tạo được (repro), đo before/after, an toàn (guardrail/confirm/fallback/rollback), grounded, ADR cho quyết định lớn.**

> "Trả lời trôi chảy" **không** được tính điểm. Phải có **eval task-success** và **chạy trong phạm vi cho phép**.

---

## 5. SLO & Error budget — phải biết đọc và xác minh

| Luồng | SLI | SLO |
|---|---|---|
| Duyệt/tìm sản phẩm | tỉ lệ non-5xx | **≥ 99.5%** |
| Duyệt — độ trễ | p95 storefront | **< 1s** |
| Giỏ hàng | tỉ lệ thao tác thành công | **≥ 99.5%** |
| **Checkout** | tỉ lệ đặt hàng thành công | **≥ 99.0%** (luồng ra tiền, ưu tiên nhất) |
| Tóm tắt AI | best-effort | **không show tóm tắt sai lệch** |

- **Error budget:** checkout ≥ 99% → budget = 1% request. Còn budget → được làm thay đổi rủi ro; cháy budget → đóng băng, ổn định lại trước. Mentor dùng khái niệm này để chấm **đánh đổi ship-nhanh vs ổn định**.
- **Cửa sổ đo:** rolling 24h cho vận hành, tổng kết theo tuần ở Ops Review. Nguồn: Prometheus/Grafana.
- **Điểm chấm quan trọng:** khi BTC bơm sự cố, mục tiêu **không phải** "SLO không bao giờ vỡ" mà là **giữ ảnh hưởng khách nhỏ nhất + phục hồi nhanh**. Cách xử lý mới là thứ được đánh giá.

Mentor nên biết cách tự dựng/đọc dashboard SLO để **kiểm chứng** con số sinh viên khai.

---

## 6. Ngân sách & Cost

- **Trần ~$300/tuần/TF** cho toàn bộ hạ tầng AWS (compute EKS/EC2, data RDS/ElastiCache/MSK hoặc EBS, mạng NAT/LB/transfer, log/metric storage, backup).
- **Vượt trần = vi phạm ràng buộc**, tính vào trụ Cost. Chi nhiều ≠ mạnh; **hiệu quả chi phí / đơn vị tải** mới được nhìn.
- Quyết định tốn tiền lớn (Multi-AZ, tăng node, managed DB) phải **cân lợi ích + ghi ADR**. "Bật Multi-AZ cho chắc" mà vỡ ngân sách = quyết định tồi.
- **Công cụ theo dõi:** AWS Cost Explorer, AWS Budgets + Cost Anomaly Detection.
- **Đánh đổi điển hình mentor sẽ vặn:** Reliability vs Cost (Multi-AZ ~gấp đôi tiền), Scale vs Cost (node lớn luôn sẵn vs autoscale+spot), Observability vs Cost (retention dài vs ngắn). **Không có đáp án đúng tuyệt đối — chấm ở đánh đổi hợp lý + giải thích được.**
- BTC có thể nới trần khi ban directive lớn (migration).

---

## 7. Cơ chế sự cố (flagd/OpenFeature) — kiến thức về luật disqualify

**Đây là phần mentor TUYỆT ĐỐI phải nắm** vì liên quan đến loại đội.

- BTC bơm sự cố qua **flagd**: flagd của TF được cấu hình **sync read-only** từ endpoint trung tâm (BTC cấp `TOKEN` qua `values-flagd-sync.yaml`). Các hook OpenFeature trong service lõi đọc flag để kích hoạt nhánh hành vi lỗi.
- **Đường dây đọc flag = hạ tầng được bảo vệ.** Gỡ/vô hiệu/refactor để service không còn đọc flag incident, re-point flagd, hay đổi hướng cơ chế = **DISQUALIFY**.
- Sinh viên **vẫn được** thêm flag/feature mới của mình — chỉ không được đụng đường dây incident.
- **Phân biệt hai loại vấn đề (mentor phải hướng dẫn đúng):**
  - **Điểm yếu do cấu hình** (thiếu sót thật) → **sửa tận gốc**.
  - **Sự cố do BTC bơm** → **làm hệ thống chịu được** (fallback/retry/containment), **KHÔNG "tắt cho hết lỗi"**.
- BTC kiểm tra định kỳ việc còn giữ đường dây flag.
- **Lưu ý deploy:** mỗi `helm upgrade` phải ghép lại `-f deploy/values-flagd-sync.yaml`, nếu không flagd rớt về local và mất kết nối trung tâm (có thể bị hiểu nhầm là đổi hướng cơ chế).

**Các điều kiện disqualify khác:** mượn kết quả TF khác; vượt ngân sách hoặc phá SLO của nhau.

---

## 8. Build → ECR → EKS → Helm — để xác minh "chạy thật"

Mentor cần đủ hiểu pipeline để **kiểm chứng hệ thống của TF đang sống**, không phải mockup.

- Mỗi TF **tự build image từ source → push ECR account mình → deploy account mình**. BTC chỉ cấp source + 1 image seed.
- **Đường A (khuyến nghị, được chấm):** `deploy/build-push-images.sh` build multi-arch (amd64+arm64), trỏ registry qua `.env.override` (`IMAGE_NAME`). Chỉ **app image** vào ECR; flagd/postgres/collector/grafana/opensearch pull từ public.
- **Đường B (bootstrap nhanh):** pull image seed `nghiadaulau/techx-corp:1.0-<svc>` → retag → push ECR. Chỉ để khởi động.
- **Chart:** `helm dependency build` (cần add đủ repo open-telemetry/grafana/prometheus/jaeger/opensearch) → `helm upgrade --install techx-corp ./techx-corp-chart -n techx-<tf>` với các values file.
- **Values file cần biết:** `values-observability.yaml`, `values-app-stamp.yaml`, `values-flagd-sync.yaml` (**bắt buộc**), `values-aio-llm.yaml` (AIO cắm LLM thật + secret `llm-api-key`), `quota.yaml`.
- **Verify hệ sống:** `kubectl get pods` (Running/Ready) → port-forward frontend-proxy 8080 → storefront hiện sản phẩm + tóm tắt AI → Grafana/Jaeger.
- **Sự cố dựng thường gặp:** image pull (sai `default.image.repository`/quyền ECR), `helm dependency build` (thiếu repo add), CrashLoopBackOff (thiếu secret llm-api-key hoặc dependency chưa Ready).

Mentor không cần tự deploy, nhưng cần đọc được `values.yaml`/`kubectl` để đánh giá cấu hình (replicas, resources, probes, security) khi chấm.

---

## 9. Observability tooling — để tự kiểm chứng lời khai

Sinh viên sẽ khai "đã giảm latency", "đã chặn tấn công", "SLO ổn". Mentor cần tự đọc telemetry để **verify**.

- Stack: OpenTelemetry → **collector** → Prometheus (metrics) · Jaeger (traces) · OpenSearch (logs) · Grafana (dashboards).
- Truy cập qua frontend-proxy: `:8080/grafana/`, `/jaeger/ui`, `/loadgen/`.
- **Kỹ năng mentor nên có:**
  - Đọc Grafana: service health, latency p95, error rate, saturation.
  - Trace một request checkout trong Jaeger để thấy nó đi qua service nào (xác minh RCA của sinh viên).
  - Xem log trong OpenSearch.
  - Với AIO: telemetry GenAI (latency/lỗi/nội dung trace của lời gọi llm) cũng đi qua đường này → verify eval/guardrail claim.
- **Nguyên tắc chấm:** số **không tái tạo được coi như chưa chứng minh**. Yêu cầu sinh viên khai rõ endpoint + kèm script `repro`.

---

## 10. Kiến thức AI/LLM — cho mentor kèm nhóm AIO (chiều sâu)

Mentor AIO cần đủ nền để phản biện kỹ thuật:

- **Eval LLM:** faithfulness/groundedness (tóm tắt khớp nguồn), task-success rate, cách xây bộ eval tái tạo được, đưa eval vào CI.
- **Guardrails:** prompt-injection (nhét lệnh trong review), PII redaction, chặn lộ system prompt, **excessive-agency** (agent không được làm hành động ngoài phạm vi).
- **RAG:** grounding trên dữ liệu thật, trích nguồn, xử lý "không có thông tin" thay vì bịa.
- **Agentic / tool-calling:** tool allow-list, confirmation gate cho hành động ghi, giới hạn vòng lặp (loop guard), audit log lời gọi tool, multi-turn context.
- **Cost/latency của LLM:** caching, model routing (rẻ vs mạnh), giảm token, timeout/retry, model gateway + A/B khi đổi model.
- **Fallback design:** khi llm lỗi/chậm → không treo trang, không show output sai.
- **AIOps:** anomaly detection đa tín hiệu, RCA cross-service, dry-run/blast-radius trước khi tự động xử lý, verify-then-rollback loop, MTTD/MTTR.

Model thật cắm được: gpt-4o-mini / Bedrock… qua `values-aio-llm.yaml` + secret. Đầu mối kỹ thuật (proto/rpc, cấu hình llm) trong `techx-corp-platform/src/product-reviews`, `src/llm`.

---

## 11. Deliverables & luật chơi — mốc chấm cụ thể

**Sản phẩm phải nộp (mentor chấm từng cái):**
1. **Backlog ưu tiên + bản pitch** (Tuần 1).
2. **Decision log / ADR ký tên** cho mọi quyết định lớn.
3. **Postmortem / COE ký tên** sau mỗi sự cố.
4. **Ops Review** hằng tuần (SLO, ngân sách, sự cố, backlog + directive đã xử).
5. **Service Health Readout** cuối kỳ + trả lời phản biện.
6. **Directive** trong `mandates/`: chấm ở **cách làm** (zero-downtime, an toàn dữ liệu, cost, bảo mật, rollback) + ADR + rollback plan — không phải chỉ "có làm xong".

**Luật chơi (mọi mentor phải thuộc):**
- Tự build từ source → ECR của TF → deploy account của TF.
- **Sự cố để xử lý, không phải để tắt.** Đụng cơ chế flagd/incident = disqualify (§7).
- Điểm yếu cấu hình → sửa gốc; sự cố bơm → làm chịu được.
- Fair play: mọi quyết định truy được về người (ký tên); không mượn kết quả TF khác.
- Tôn trọng ràng buộc: không vượt ngân sách, không phá SLO của nhau.

---

## 12. Rubric — Phase 3 chấm judgment nhiều hơn code

Xuyên suốt, năm chiều đánh giá (áp cho cả CDO lẫn AIO):

1. **Ưu tiên & judgment** — chọn đúng việc đáng làm, **dám bỏ việc tác động thấp** và giải thích được.
2. **Engineering & Ops** — xử lý đúng gốc, không tạo lỗi mới, có đo before/after.
3. **Business trade-off** — quy quyết định về chi phí / khách hàng / SLO.
4. **Năng lực chuyên môn** — CDO: 5 trụ; AIO: AIOps + AIE.
5. **Communication** — ADR/postmortem rõ ràng, quản lý stakeholder khi bị phản biện.

**Nguyên tắc verify khi chấm:** chạy thật không mockup · số liệu tái tạo được (`repro`) · đo before/after · an toàn (guardrail/confirm/fallback/rollback) · quyết định lớn có ADR · không phá SLO/ngân sách.

---

## 13. Kỹ năng đóng vai hội đồng phản biện

Ở **Pitch (cuối Tuần 1)** và **Health Readout (cuối kỳ)**, mentor/BTC đóng vai 3 stakeholder trái chiều để stress-test tư duy. Mentor cần biết vặn theo vai:

| Vai | Quan tâm | Câu hỏi mẫu để vặn |
|---|---|---|
| **PM** | Khách hàng, trải nghiệm | "Tuần này khách được gì? Sao lo hạ tầng mà không cải thiện thứ khách thấy?" |
| **CFO** | Chi phí, ROI | "Tốn bao nhiêu? Trong ~$300/tuần chịu nổi không? Chứng minh đáng tiền." |
| **SRE lead** | Reliability, rủi ro | "Rủi ro gì? Đã test drain/failover chưa? Readiness threshold set bao nhiêu? Sai thì sao?" |

**Cách chấm ở buổi phản biện:**
- Ưu tiên = **Rủi ro (khả năng × mức nghiêm trọng) × Tác động business** (đo bằng SLO/BUDGET/INCIDENT_HISTORY/ARCHITECTURE — **không phải** "có phải feature hay không").
- Điều được nhìn: sinh viên **giữ được lập luận, có số liệu, điều chỉnh hợp lý khi bị phản biện** — hay lúng túng, bảo vệ bằng cảm tính.
- **Bỏ đúng việc cũng là kỹ năng được chấm** (cố ý deprioritize gì và vì sao).
- Ở Health Readout: hội đồng có thể **hỏi thẳng một cá nhân** để kiểm chứng chiều sâu — mentor cần biết đội có hiểu thật hay chỉ một người làm.

---

## 14. Checklist nhanh cho mentor trước khi chấm

- [ ] Đã đọc `RULES.md` + toàn bộ `onboarding/` + `GETTING_STARTED.md`.
- [ ] Biết TF mình kèm gồm nhóm nào, mỗi nhóm sở hữu trụ nào (CDO) / hướng nào (AIO).
- [ ] Nắm điều kiện **disqualify** (đụng flagd/incident, mượn kết quả, phá SLO/ngân sách nhau).
- [ ] Truy cập được Grafana/Jaeger/OpenSearch của TF để tự verify số liệu.
- [ ] Xác minh hệ thống TF **đang chạy thật** (pods Ready, storefront + tóm tắt AI sống).
- [ ] Với AIO: có endpoint tính năng AI + kênh cảnh báo AIOps + bộ eval/`repro`.
- [ ] Kiểm tra mọi quyết định lớn có **ADR ký tên**; mỗi sự cố có **postmortem**.
- [ ] Xác minh **không vượt ngân sách ~$300/tuần** + SLO còn trong ngưỡng (hoặc phục hồi hợp lý).
- [ ] Chuẩn bị câu hỏi phản biện theo 3 vai (PM/CFO/SRE) cho Pitch & Health Readout.
- [ ] Theo dõi `mandates/` để biết directive đã ban và chấm cách TF thực thi.
```
