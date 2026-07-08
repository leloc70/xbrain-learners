# Guide — Trụ Auditability (Phase 3)

Hướng dẫn cho **mentor** (coach + chấm) và **HV** về trụ **Auditability** — trụ xuyên suốt mọi thay đổi. Bám hiện trạng thật của repo (đã điều tra `values.yaml`, `serviceaccount.yaml`, `demo.proto`). Đọc kèm `GRADING_DEEPDIVE.md` §3.5 và `PROJECT_INVESTIGATION.md` §C.5.

> **Một câu định nghĩa:** Auditability = **truy được AI làm GÌ, KHI NÀO, và CHỨNG MINH được** — trên cả 3 mặt: hạ tầng AWS, cụm Kubernetes, và ứng dụng/dữ liệu. Xuyên suốt vì mọi thay đổi của 4 trụ kia đều phải để lại dấu vết.

---

## 1. Vì sao trụ này đặc biệt

- **Nhẹ hơn nhưng xuyên suốt:** trong TF 2 CDO, hai nhóm **luân phiên** cầm Auditability mỗi tuần; trong TF 3 CDO, **một nhóm đào sâu**. Không nhóm nào "sở hữu độc quyền" — mọi thay đổi của Security/Reliability/Cost/Perf đều sinh ra artifact audit.
- **Nó chính là thứ nuôi việc chấm cá nhân:** ADR/decision-log **ký tên**, COE/postmortem, ca on-call — đây vừa là deliverable của trụ Audit, vừa là **bằng chứng quy-về-tên** mà mentor dùng chấm individual (xem JD Individual Assessor). Làm tốt Audit = làm chính điểm cá nhân của cả TF **truy được**.
- **Ranh giới disqualify:** flagd/đường dây incident là hạ tầng được bảo vệ. Audit **ghi lại** thao tác lên flag của mình thì tốt, nhưng **không được** refactor/gỡ hook đọc flag nhân danh "dọn audit".

---

## 2. Hiện trạng repo — audit gần như bằng 0 (gap để HV nhìn ra)

| Mặt | Hiện trạng (đọc từ config) | Hệ quả |
|---|---|---|
| Change management | Deploy bằng `helm upgrade` **tay**, không GitOps; **chưa có ADR/decision-log/postmortem template** trong repo | Không truy được "ai đổi gì khi nào" |
| Danh tính cụm | **1 ServiceAccount dùng chung** (`serviceaccount.yaml`), **không Role/ClusterRole/RBAC nào**; chưa IRSA | Mọi pod cùng danh tính → không attribute được hành động |
| K8s audit | **Không** audit policy cho API server | Thao tác lên cụm không có dấu vết |
| AWS audit | **Không** thấy CloudTrail/Config wiring trong repo | Thao tác AWS API không truy được |
| Log integrity | OpenSearch `DISABLE_SECURITY_PLUGIN: true` — **không auth**, `persistence:false` | Log sửa/mất được, không tin cậy làm bằng chứng |
| Truy cập UI | Grafana `auth.anonymous + org_role: Admin`, `disable_login_form:true` | **Ai cũng là admin** → không biết ai xem/sửa gì |
| App/data audit | Không có audit log cho thao tác nhạy cảm; `FeatureFlagService` có `CreateFlag/UpdateFlag/DeleteFlag` nhưng không log ai gọi | Mutation không dấu vết |

> Đây là **lỗ hổng cấu hình** (không phải sự cố bơm) → HV phải **sửa tận gốc**, sửa là được điểm.

---

## 3. Bốn lớp Audit cần phủ + target tối ưu

### Lớp 1 — Change Management (dấu vết thay đổi hệ thống)
- **GitOps (ArgoCD/Flux)** thay `helm upgrade` tay → mọi thay đổi hạ tầng = **commit ký tên**, có review, rollback bằng git revert.
- **ADR / decision-log ký tên** cho mọi quyết định lớn: context → options → trade-off có số → quyết định → hệ quả/rollback → **tên + thời điểm**.
- **Postmortem/COE ký tên** sau mỗi sự cố (timeline, MTTD/MTTR, root cause, action item).
- Chart versioning + `revisionHistoryLimit` (đã có) để truy rollout history.

### Lớp 2 — AWS / Infrastructure audit
- **CloudTrail** bật (management + data events cho S3/ECR/Secrets) → CloudWatch/S3, bật **log file validation** (chống sửa).
- **AWS Config** ghi lại thay đổi cấu hình resource + compliance rules.
- Budgets/Cost Anomaly (giao với Cost) cũng là dấu vết chi tiêu bất thường.

### Lớp 3 — Kubernetes audit + danh tính
- **API server audit policy** (EKS control-plane logging → CloudWatch): ai gọi API nào, verb gì, khi nào.
- **RBAC least-privilege:** tách ServiceAccount **theo workload** (thay vì 1 SA chung), Role/RoleBinding tối thiểu; **IRSA** để pod có danh tính AWS riêng, truy được.
- Không dùng `cluster-admin` bừa; kiểm bằng `kubectl auth can-i --list`.

### Lớp 4 — Application / Data audit + Log integrity
- **OpenSearch bật security plugin** (auth + RBAC) + **retention** + persistence → log tin cậy làm bằng chứng.
- **Immutable/append-only** cho audit log nhạy cảm; đồng bộ đồng hồ (timestamp tin cậy).
- **PII handling** trong log (không log thô dữ liệu khách).
- **(AIO) Audit log mọi tool-call của Shopping Copilot** — ai/phiên nào gọi tool ghi (AddItem…), khi nào; đây là yêu cầu bắt buộc của agent (excessive-agency).
- Log thao tác mutation (`CreateFlag/UpdateFlag/DeleteFlag` nếu TF thêm flag của mình).

---

## 4. Cách CHẤM trụ Auditability (bằng chứng · verify · red flag)

**Bằng chứng "làm thật" phải đòi:**
- Truy **một thay đổi bất kỳ** về commit + người + thời điểm (qua GitOps/ADR).
- CloudTrail trả về được **một API call cụ thể** (ai, khi nào).
- EKS audit log có bản ghi thao tác cụm; RBAC không còn 1-SA-chung.
- OpenSearch có auth; thử sửa/xóa log bị chặn hoặc phát hiện được.
- (AIO) audit log tool-call của agent tồn tại và đọc được.

**Cách mentor tự verify:**
```
git log --format='%h %an %ad %s' <file cấu hình>      # thay đổi truy về người?
kubectl get sa,role,rolebinding -n techx-<tf>          # còn 1 SA chung không?
kubectl auth can-i --list --as=system:serviceaccount:techx-<tf>:<sa>
# CloudTrail: tìm 1 event (vd PutObject/UpdateSecret) → ai gọi
# Grafana: mở ẩn danh → còn vào được admin không?
# OpenSearch: gọi API không token → bị 401 chưa?
```

**Red flag (trừ điểm):**
- Deploy tay không dấu vết; ADR viết **lấp sau** khi làm (lộ khi bị hỏi walk-through).
- Grafana vẫn anonymous admin → không truy được ai làm gì.
- Vẫn 1 ServiceAccount chung, RBAC allow-all.
- Audit log để plaintext, sửa được, không retention → **không tin cậy làm bằng chứng**.
- Postmortem đổ lỗi "do BTC bơm flag", không action item.

**Thang mức (theo rubric 5 mức):**
- **1–2:** không dấu vết, deploy tay, ADR hình thức.
- **3:** có ADR ký tên + một phần audit (vd EKS audit log bật) nhưng rời rạc, chưa truy xuyên suốt.
- **4:** GitOps + CloudTrail + K8s audit + RBAC tách, truy được end-to-end một thay đổi.
- **5:** như 4 + log integrity (immutable/retention/auth) + audit tool-call AI + chứng minh live khi bị hỏi bất kỳ thay đổi nào.

---

## 5. Coaching — hỏi gì khi HV làm trụ này (không giải hộ)

- *"Một thay đổi bất kỳ tuần này, em truy được về ai + khi nào không? Bằng gì?"*
- *"Nếu mai có người xoá nhầm cấu hình, em biết ai làm sau bao lâu?"*
- *"Log của em có tin cậy làm bằng chứng không — ai sửa được nó?"*
- *"Mọi pod đang chung một danh tính; thao tác lên AWS thì quy về ai?"*
- *"Audit tốn gì (storage/retention)? Cân với ngân sách thế nào?"* (giao Cost)
- *"ADR này viết trước hay sau khi làm? Walk-through cho anh quyết định trong đó."*

> Nhắc HV: Auditability **rẻ và tác động cao** để đưa vào backlog PRR — nó bảo vệ mọi trụ khác và chính điểm cá nhân của cả đội. Nhưng đừng làm nặng nề tới mức phá ngân sách (retention dài vô tội vạ).

---

## 6. Giao thoa với trụ khác & deliverables

- **↔ Security:** RBAC/IRSA/least-privilege vừa là Security vừa là Audit; log auth (OpenSearch/Grafana) chung cả hai.
- **↔ Cost:** retention/storage của audit log phải cân trần ~$300/tuần — đánh đổi giữ log lâu vs chi phí.
- **↔ Reliability/Perf:** mọi thay đổi (probe, replica, autoscale) đều sinh ADR + rollout history.
- **↔ Chấm cá nhân:** ADR ký tên + COE + on-call chính là input scorecard 6 chiều — Audit tốt làm attribution rõ, gỡ đúng chỗ mentor đuối nhất (free-rider/single-contributor).

**Deliverable của trụ (kiểm ở Ops Review & Readout):** GitOps repo/pipeline, ADR/decision-log ký tên, postmortem/COE, bằng chứng CloudTrail + EKS audit + RBAC, cấu hình log integrity, (AIO) audit log tool-call.
