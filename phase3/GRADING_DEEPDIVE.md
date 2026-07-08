# Đào sâu: các phần phải chấm điểm — Phase 3

Tài liệu chấm chi tiết cho mentor/hội đồng. Khác với `MENTOR_GRADING_GUIDE.md` (tổng quan kiến thức), file này **đào sâu từng phần được chấm**: bằng chứng phải đòi, cách tự verify, thang điểm theo mức, và red flag. Mọi tiêu chí đã gắn với **hiện trạng thật** của hệ thống (xem `PROJECT_INVESTIGATION.md`).

> **Triết lý xuyên suốt:** Phase 3 chấm **judgment > code**. Câu hỏi lõi cho mọi hạng mục: *"Có nhìn ra đúng việc không? Có đo before/after không? Có quy về khách/tiền/SLO không? Có truy được về người (ADR) không? Có an toàn (không phá SLO/ngân sách/flagd) không?"*

---

## 0. Bản đồ trọng số đề xuất

Không có barem cứng từ BTC — đây là gợi ý phân bổ để chấm nhất quán. Mentor/BTC chốt lại trước khi chấm.

| Khối chấm | Trọng số gợi ý | Mốc thu thập bằng chứng |
|---|---|---|
| **Judgment & Ưu tiên** (backlog + pitch + bỏ đúng việc) | 25% | Pitch cuối T1, Health Readout |
| **Engineering & Ops** (chất lượng kỹ thuật, đo before/after) | 20% | Vận hành T2-3, Ops Review |
| **Xử lý sự cố** (phát hiện/containment/recovery/postmortem) | 20% | Trong lúc vận hành (flag bơm) |
| **Năng lực chuyên môn** (5 trụ CDO / AIOps+AIE cho AIO) | 20% | Toàn kỳ, verify trên hệ chạy thật |
| **Business trade-off & Communication** (ADR, quản lý stakeholder khi bị vặn) | 15% | Pitch, Ops Review, Health Readout |

**Nhân tử phạt (áp sau khi cộng điểm):**
- Vi phạm disqualify (§8) → **loại**, không chấm tiếp.
- Vượt ngân sách / phá SLO của TF khác → trừ nặng trụ Cost/Reliability.
- Số liệu **không tái tạo được** (`repro`) → coi như **chưa chứng minh**, không tính điểm hạng mục đó.

---

## 1. Chấm theo mốc thời gian (checkpoint nào chấm gì)

### 1.1 Baseline chạy được (đầu T1) — pass/fail có điểm
**Phải verify tận tay:** `kubectl -n techx-<tf> get pods` tất cả Running/Ready · storefront :8080 đặt được 1 đơn end-to-end · trang sản phẩm có tóm tắt AI · Grafana/Jaeger/loadgen mở được.
- **Đạt:** hệ sống, image build từ source đẩy ECR của TF (không xài thẳng seed public).
- **Red flag:** dùng nguyên image seed `nghiadaulau/*` không build lại (bỏ lỡ kỹ năng CI được chấm); flagd không sync central (thiếu `-f values-flagd-sync.yaml`).

### 1.2 Pitch bảo vệ ưu tiên (cuối T1) — mốc judgment quan trọng nhất
Xem §5.1 (rubric backlog) + §7 (đóng vai phản biện).

### 1.3 Weekly Ops Review — nhịp kiểm tra
Mỗi tuần phải trình: trạng thái SLO (số thật từ Grafana), tiêu ngân sách so trần, sự cố đã xử + MTTD/MTTR, backlog & directive đã đóng. **Chấm:** có dựa trên số đo thật không, hay kể chuyện định tính.

### 1.4 Service Health Readout (cuối kỳ)
Trình: đã làm gì · đánh đổi gì & vì sao · trạng thái service · tiếp theo. Hội đồng phản biện, **hỏi thẳng cá nhân** để kiểm chứng chiều sâu (chống một người làm cả nhóm).

---

## 2. Rubric 5 chiều (thang 5 mức) — áp cho MỌI hạng mục

Dùng ma trận này để chấm nhất quán từng deliverable/quyết định.

| Chiều | 1 — Kém | 3 — Đạt | 5 — Xuất sắc |
|---|---|---|---|
| **Ưu tiên & Judgment** | làm việc dễ/thích, không xếp hạng | có xếp hạng nhưng lý do mỏng | xếp theo rủi ro×business, **dám bỏ việc tác động thấp và giải thích được** |
| **Engineering & Ops** | sửa vá, tạo lỗi mới, không đo | sửa đúng nhưng thiếu đo before/after | sửa tận gốc + đo before/after + repro được + không hồi quy |
| **Business trade-off** | quyết định "cho chắc", không nhắc tiền/khách | có nhắc chi phí/SLO chung chung | quy rõ về $/khách/SLO/error-budget, chọn có con số |
| **Năng lực chuyên môn** | sai khái niệm trụ/AI | đúng chuẩn, làm được cơ bản | sâu, đúng best practice, xử lý được ca khó |
| **Communication** | không ADR, bảo vệ bằng cảm tính | có ADR sơ sài, giữ được cơ bản khi bị hỏi | ADR/postmortem rõ, **điều chỉnh hợp lý khi bị phản biện**, quản lý stakeholder |

---

## 3. Chấm năng lực theo TRỤ (CDO) — bằng chứng + cách verify + red flag

Mỗi trụ: (a) **bằng chứng "làm thật" phải đòi**, (b) **cách mentor tự verify**, (c) **red flag trừ điểm**. Gắn với hiện trạng đã điều tra.

### 3.1 Reliability (trụ nặng nhất — checkout ra tiền)
**Bằng chứng đòi:**
- Checkout path (`checkout/cart/payment/product-catalog/frontend/frontend-proxy`) đã **≥2 replica + readiness/liveness probe + PDB + spread AZ/node**.
- Resilience: timeout/retry-jitter/circuit-breaker/idempotency ở caller (đặc biệt checkout→payment).
- State bền: valkey/postgres/kafka có persistence hoặc lên managed (đóng INC-2), có backup/restore chứng minh.
- Kết quả **chịu được** flag: `paymentFailure`, `cartFailure`, `failedReadinessProbe`, `kafkaQueueProblems`, `emailMemoryLeak`.

**Verify:** `kubectl get deploy -o wide` (replicas), `kubectl describe pod` (probe), `kubectl get pdb`; xem Grafana SLO checkout khi flag đang bật; drain 1 node xem giỏ có mất không.

**Red flag:** vẫn `replicas: 1` toàn hệ (baseline chưa động); "sửa" bằng cách restart tay; tắt/né flag thay vì làm chịu được → **disqualify**; Multi-AZ bật "cho chắc" phá ngân sách.

### 3.2 Performance Efficiency
**Bằng chứng:** `requests+limits` (CPU+mem) mọi service; **HPA** cho frontend/catalog/recommendation; autoscaler/Karpenter; load-shedding/rate-limit ở Envoy. Load test **before/after** (p95, throughput, error) dưới `loadGeneratorFloodHomepage`/`adHighCpu`.

**Verify:** `kubectl get hpa`, `kubectl top pod`; chạy loadgen tăng tải xem HPA scale + p95 giữ <1s (SLO duyệt), error<0.5%.

**Red flag:** chỉ đặt limit không requests (baseline hiện tại); "tối ưu" mà không có số tải chứng minh; scale tay.

### 3.3 Cost Optimization (~$300/tuần/TF)
**Bằng chứng:** AWS Budgets + Cost Anomaly Detection bật sớm; right-size **bằng số Prometheus/VPA thật** (không đoán); spot cho stateless; trace sampling + retention tiering; ADR cho mọi quyết định tốn tiền lớn. Chỉ số **hiệu quả chi phí / đơn vị tải** (cost per 1k orders).

**Verify:** Cost Explorer theo service/ngày; đối chiếu requests vs usage thật; kiểm tra có vượt trần không.

**Red flag:** chi nhiều = mạnh (sai); Multi-AZ/node lớn không ROI; **vượt trần** (trừ nặng); cắt observability tới mức mất khả năng đo (đánh đổi tồi).

### 3.4 Security (hardening lỗ cấu hình — sửa tận gốc)
**Bằng chứng đòi (gắn lỗ đã tìm):** bỏ mật khẩu hardcode (`postgres root/otel`, `otelu/otelp`) → Secret/External-Secrets/SSM + IRSA; bật TLS (`sslmode=require`, Kafka SASL/TLS); OpenSearch bật lại security plugin; Grafana tắt anonymous-admin + đổi `adminPassword: admin`; pod hardening (`runAsNonRoot`, `readOnlyRootFilesystem`, drop caps) cho các service đang chạy root; **NetworkPolicy** least-privilege; image scan (Trivy) + pin digest.

**Verify:** `kubectl get secret` (không còn plaintext env), `kubectl get networkpolicy`, `kubectl get pod -o jsonpath` securityContext; thử `psql` không TLS xem bị chặn; mở Grafana ẩn danh xem còn admin không.

**Red flag:** coi lỗ cấu hình là "sự cố bơm" và bỏ qua; đổi mật khẩu nhưng vẫn hardcode chỗ khác; NetworkPolicy allow-all.

### 3.5 Auditability (xuyên suốt, luân phiên)
**Bằng chứng:** GitOps (ArgoCD/Flux) thay `helm upgrade` tay → thay đổi có commit ký tên; EKS control-plane audit log → CloudWatch; CloudTrail bật; OpenSearch có auth + retention; **ADR/decision-log/postmortem template** tồn tại và được dùng thật.

**Verify:** truy 1 thay đổi bất kỳ về commit + người; mở CloudTrail tìm 1 API call; kiểm log integrity.

**Red flag:** deploy tay không dấu vết; Grafana anonymous admin (không truy được ai làm gì); ADR viết lấp sau khi làm.

---

## 4. Chấm tầng AI (AIO) — đào sâu

Hai hướng, chấm trên **hệ chạy thật + eval tái tạo được**. "Trả lời trôi chảy" **không** tính điểm.

### 4.1 AIE — Phần A: nâng chất tóm tắt review
**Bằng chứng đòi:**
- Đã **cắm LLM thật** (`values-aio-llm.yaml` + secret), không còn mock.
- **Faithfulness eval** (bộ dữ liệu + script `repro`) chứng minh tóm tắt khớp review gốc; **đặc biệt chặn được ca `llmInaccurateResponse` cho product `L9ECAV7KIM`** — hệ thống hiện sẵn sàng show sai, agent/guardrail phải chặn.
- **Guardrail:** prompt-injection nhét trong review, PII redaction, chặn lộ system prompt — có test case + tỉ lệ chặn.
- **Fallback/cost:** xử lý `llmRateLimitError` (429 ~50%) bằng retry/backoff + cache + graceful fallback (không show chuỗi lỗi thô như baseline); đo token/latency/cost before-after.

**Verify:** bật cờ `llmInaccurateResponse` (trong môi trường test của TF) xem khách có thấy tóm tắt sai không; chạy script eval của TF; xem trace GenAI trong Jaeger (latency/lỗi/nội dung).

**Red flag:** eval là ảnh chụp không chạy lại được; "fallback" chỉ là try/except trả chuỗi cứng; đo bằng cảm nhận.

### 4.2 AIE — Phần B: Shopping Copilot agentic (tự dựng)
**3 intent core phải chạy thật** (wire vào RPC có sẵn: `SearchProducts`, `GetProductReviews/AskProductAIAssistant`, `CartService.AddItem/GetCart`):

| Intent | "Done" để tính điểm |
|---|---|
| NL search | query tự nhiên ("tai nghe chống ồn <$50") ra đúng SP, không phải keyword khớp cứng |
| RAG grounded | trả lời từ review thật, **nói "không có thông tin"** khi review không đề cập — 0 hallucinate |
| Cart có kiểm soát | thực thi đúng lệnh, **confirmation trước khi ghi**, **không tự checkout/EmptyCart** |

**Yêu cầu xuyên suốt (đều chấm):** multi-turn nhớ ngữ cảnh; **tool allow-list**; **confirmation gate** cho hành động ghi (guardrail **excessive-agency** — cấm EmptyCart/PlaceOrder tự động); grounded không lộ PII/system prompt; **loop guard**; **audit log mọi tool call**; fallback khi LLM lỗi.
**Bắt buộc:** **eval task-success** tái tạo được (không phải demo 1 lần).

**Verify:** tương tác trực tiếp agent trên hệ TF; thử ép nó checkout/xoá giỏ (phải từ chối/hỏi xác nhận); hỏi câu review không có (phải nói không biết); xem audit log tool call.

**Red flag:** agent tự checkout/xoá giỏ (**excessive-agency — trừ nặng, gần disqualify về an toàn**); bịa thông tin; không có eval; chạy mockup không deploy.

### 4.3 AIOps — dùng AI vận hành hệ thống
**Bằng chứng:** vòng phát hiện bất thường đa tín hiệu (latency/error/saturation/queue-lag/cost) trên Prometheus/Jaeger/OpenSearch → kiểm tra an toàn (dry-run/blast-radius) → xử lý → verify qua telemetry → rollback/escalate. **Bar cao = chạy liên tục + xử lý được sự cố thật**, không demo một lần. Có endpoint/kênh cảnh báo khai rõ; đo **MTTD/MTTR** before-after.

**Verify:** bơm 1 flag sự cố, xem hệ AIOps có phát hiện + hành động + verify không; xem log/kênh alert.

**Red flag:** "AIOps" chỉ là 1 alert rule tĩnh; hành động không có safety check (blast radius); tự động can thiệp vào đường dây flagd → disqualify.

---

## 5. Chấm DELIVERABLES (từng sản phẩm nộp)

### 5.1 Backlog ưu tiên + Pitch (T1)
**Chấm:** mỗi dòng backlog quy được về **Rủi ro (khả năng×nghiêm trọng) × Business (SLO/BUDGET/INCIDENT/ARCH)**; có top-N xếp hạng rõ; **nêu rõ cố ý bỏ gì và vì sao**.
- **Xuất sắc:** ưu tiên khớp rủi ro thật của hệ (checkout SPOF, mất giỏ, secret hở), có ước lượng chi phí trong trần, giữ lập luận khi bị vặn.
- **Kém:** backlog toàn feature "khách thấy" mà bỏ SPOF luồng tiền; xếp hạng theo độ dễ; không dám bỏ gì.

### 5.2 ADR / Decision log (ký tên)
**Chấm mỗi ADR:** context → options → **trade-off có số** (tiền/SLO/rủi ro) → quyết định → hệ quả/rollback. Truy được về người + thời điểm.
- **Red flag:** ADR viết lấp sau khi làm; "chọn X vì tốt hơn" không số; không rollback plan.

### 5.3 Postmortem / COE (sau mỗi sự cố)
**Chấm:** timeline (detect→mitigate→resolve) + **MTTD/MTTR** + root cause thật (phân biệt lỗ cấu hình vs flag bơm) + **action item chống tái diễn** + ký tên. Blameless.
- **Red flag:** đổ lỗi "do BTC bơm flag"; không có action item; không số MTTD/MTTR.

### 5.4 Weekly Ops Review
**Chấm:** dựa trên **số đo thật** (SLO từ Grafana, cost từ Cost Explorer), không định tính; trạng thái error budget; tiến độ backlog/directive.

### 5.5 Directive từ `mandates/` (T2-3)
**Chấm ở CÁCH làm, không phải "có xong":** zero-downtime, an toàn dữ liệu (migration có backup+verify), cost trong trần, bảo mật, **rollback plan** + ADR. Ví dụ directive điển hình: migrate postgres → RDS.
- **Red flag:** migrate mất data/downtime; không rollback; không cân cost.

### 5.6 Service Health Readout (cuối kỳ)
**Chấm:** trình bày trung thực (test fail thì nói fail), đánh đổi rõ, trạng thái service có số; **cá nhân bị hỏi thẳng vẫn trả lời được** (chiều sâu thật của cả nhóm).

---

## 6. Chấm XỬ LÝ SỰ CỐ — "good looks like" cho từng flag

Sự cố bơm là để **chịu được**, không phải tắt. Với mỗi flag, chấm: **phát hiện nhanh (MTTD)** → **containment giữ khách ít ảnh hưởng** → **recovery (MTTR)** → **postmortem + action item**. Bảng chuẩn "đạt":

| Flag bơm | "Đạt" trông thế nào | Trụ |
|---|---|---|
| `paymentFailure` / `paymentUnreachable` | checkout retry/circuit-break, degrade có kiểm soát, không mất đơn im lặng | Reliability |
| `cartFailure` / `failedReadinessProbe` | multi-replica + probe đúng → traffic né pod hỏng, giỏ không mất | Reliability |
| `kafkaQueueProblems` | phát hiện lag qua metric, scale consumer/backpressure/DLQ, accounting không kẹt | Reliability/Perf |
| `emailMemoryLeak` | memory limit + restart, email không kéo checkout chết (async/degrade) | Reliability |
| `loadGeneratorFloodHomepage` | HPA scale + rate-limit/load-shed, p95 giữ, SLO duyệt không vỡ | Perf |
| `adHighCpu`/`adManualGc`/`adFailure` | CPU limit + timeout, ad lỗi **không** làm trang sản phẩm chết (degrade) | Perf/Reliability |
| `productCatalogFailure` | caller timeout/retry/circuit-break, chỉ 1 product lỗi không sập trang | Reliability |
| `recommendationCacheFailure` | degrade gracefully, trang vẫn load không rec | Reliability |
| `imageSlowLoad` | timeout + lazy load, không block render | Perf |
| `llmInaccurateResponse` | guardrail/eval chặn show tóm tắt sai cho khách | AIE |
| `llmRateLimitError` | retry/backoff + cache + fallback graceful | AIE |

**Nguyên tắc chấm chung:** phát hiện bằng telemetry (không phải khách báo); containment trước, root-cause sau; **không đụng flagd**; có postmortem.

---

## 7. Đóng vai hội đồng phản biện — bộ câu hỏi để chấm chiều sâu

Vặn theo vai để lộ tư duy. Chấm ở khả năng **giữ lập luận có số + điều chỉnh hợp lý**, không phải "trả lời trơn".

**CFO (tiền):** "Thay đổi này tốn bao nhiêu/tuần? Trong ~$300 chịu nổi? ROI? Cost per 1k orders trước-sau?"
**SRE (rủi ro):** "Probe threshold bao nhiêu? Test drain/failover chưa? Rollback thế nào? Nếu sai thì blast radius tới đâu?"
**PM (khách):** "Tuần này khách được gì? Sao lo hạ tầng trước feature? Đánh đổi trải nghiệm ở đâu?"
**Đào cá nhân (Health Readout):** hỏi 1 người về chi tiết kỹ thuật của phần nhóm khai — kiểm chứng không phải một người làm tất.

**Chấm:** có số liệu hậu thuẫn (5) vs cảm tính (1); thừa nhận giới hạn & điều chỉnh (5) vs phòng thủ cứng/lúng túng (1).

---

## 8. Checklist DISQUALIFY (kiểm trước khi chấm điểm)

Vi phạm bất kỳ mục nào → **loại khỏi vòng đánh giá**, không chấm tiếp:
- [ ] Gỡ/vô hiệu/refactor để service **không còn đọc flag incident** (OpenFeature hook).
- [ ] Re-point flagd khỏi nguồn central của BTC / bỏ `values-flagd-sync.yaml`.
- [ ] Can thiệp, tắt, hay đổi hướng cơ chế tạo sự cố bằng bất kỳ cách nào.
- [ ] Mượn/nộp kết quả của TF khác.
- [ ] Vượt ngân sách hoặc **phá SLO của TF khác**.

**Phân biệt then chốt khi chấm:** *lỗ hổng do cấu hình* (secret hardcode, thiếu probe, replicas:1...) → **phải sửa tận gốc**, sửa là được điểm. *Sự cố do flag bơm* → **phải làm hệ thống chịu được** (fallback/retry/containment), **tắt flag để "hết lỗi" = disqualify**.

---

## 9. Scoring sheet mẫu (điền cho mỗi nhóm)

```
Nhóm: ______   TF: ___   Trụ sở hữu / hướng AIO: ______________

A. Judgment & Ưu tiên (25)   ___/25   ghi chú: backlog quy về risk×business? dám bỏ đúng?
B. Engineering & Ops (20)    ___/20   sửa gốc? đo before/after? repro?
C. Xử lý sự cố (20)          ___/20   MTTD/MTTR? containment? postmortem+action item?
D. Chuyên môn trụ/AI (20)    ___/20   verify trên hệ chạy thật (§3/§4)
E. Business & Comm (15)      ___/15   ADR có số? giữ lập luận khi bị vặn?
                             --------
   Tổng thô                  ___/100

Phạt: [ ] vượt ngân sách  [ ] số không repro (loại hạng mục)  [ ] phá SLO nhóm khác
DISQUALIFY (§8): [ ] có → DỪNG, không chấm

Verify đã làm: [ ]pods Ready [ ]SLO Grafana [ ]cost Explorer [ ]AI endpoint+eval [ ]ADR/postmortem
```

> Con số trọng số là gợi ý — chốt với BTC trước khi chấm để 13 mentor chấm cùng thước.
