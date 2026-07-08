# W1 Grading Checklist — Mentor Chấm Cá Nhân (Phase 3)

Checklist điền được cho **từng học viên (HV)** trong Tuần 1 ("Takeover & PRR"). Dựa trên JD _Individual Assessor_: chấm **cá nhân độc lập, double-blind**, **bắt buộc dẫn chứng từng chiều**, không tính verbal claim.

**Cách dùng:**
- Mỗi HV một bản (copy khối §3 → §6). Điền suốt tuần, chốt tại **PRR (T6 W1)**.
- Likert **1–5** theo behavioral anchor (§2). Ô **Dẫn chứng bắt buộc** trống = **không được chấm >3**.
- 2 mentor chấm riêng, không xem điểm nhau. **Lệch ≥1.0 ở bất kỳ chiều → re-discuss.**
- W1 chưa có incident/COE thật → chiều 4 chấm ở mức *nhận diện & kế hoạch*, chưa phải *thực thi dưới sự cố*.

---

## 1. Thông tin & mốc quan sát

```
HV: __________________  Cohort: [ ] CDO  [ ] AIO   Nhóm/TF: ______  Trụ own (CDO)/Hướng (AIO): __________
Mentor chấm: __________________   Ngày chốt (T6 W1): __________

Mốc đã quan sát HV này trong W1:
[ ] Daily standup / on-call handoff   số buổi: ___
[ ] Check-up cá nhân                  số buổi: ___
[ ] PRR (T6 W1)  — bắt buộc
[ ] Ca on-call đầu tiên               ngày: ___
```

---

## 2. Behavioral anchor (thang 1–5 dùng cho mọi chiều)

| Mức | Ý nghĩa |
|---|---|
| **1** | Sai/thiếu; không có dẫn chứng; verbal claim |
| **2** | Có làm nhưng nông; lệ thuộc người khác dẫn |
| **3** | Đạt chuẩn; làm được phần cơ bản; có dẫn chứng tối thiểu |
| **4** | Vững; có đo/lý do; chủ động; dẫn chứng rõ quy về tên |
| **5** | Xuất sắc; quy về risk×business có số; giữ lập luận khi bị vặn; dẫn dắt |

> Không có dẫn chứng repo/live/ADR ký tên ⇒ trần điểm = **3**.

---

## 3. Nguồn tín hiệu cá nhân W1 (thu trước — để quy về tên)

Đánh dấu cái nào **thực sự có** cho HV này (kèm link/đường dẫn):

```
[ ] ADR/decision-log KÝ TÊN            → __________________________  (quyết định gì: ________)
[ ] Backlog item HV đề xuất/own        → __________________________
[ ] Commit/PR trong W1 (build/deploy/hardening/dashboard) → ________________________
[ ] Vai trò tại PRR (trình phần nào)   → __________________________
[ ] Ca on-call + chất lượng handoff    → __________________________
```

Attribution note (gỡ mờ do DRI rotation): ________________________________________________

---

## 4. Chấm 6 chiều (Mentor Scorecard) — trọng tâm W1

> Cột "Tín hiệu W1" cho biết chiều đó **mạnh/vừa** ở tuần này. Chiều mạnh cần chấm kỹ hơn.

### Chiều 1 — Judgment & Prioritization  *(W1: MẠNH)*
Nhìn ra đúng rủi ro lớn (SPOF checkout, `replicas:1` toàn hệ, mất giỏ, secret hardcode); backlog xếp theo **rủi ro × business**; **dám bỏ đúng việc tác động thấp và giải thích được**.
```
Điểm: [1] [2] [3] [4] [5]
Dẫn chứng bắt buộc: ______________________________________________________________
```

### Chiều 2 — Engineering & Ops Excellence  *(W1: VỪA)*
Baseline **build-from-source → ECR → deploy live** chạy thật (không xài thẳng seed); dashboard SLO dựng sớm; hardening đầu có đo before/after; sửa gốc không vá ẩu.
```
Điểm: [1] [2] [3] [4] [5]
Dẫn chứng bắt buộc: ______________________________________________________________
```

### Chiều 3 — Product & Business Trade-off  *(W1: MẠNH — qua PRR)*
Quy quyết định về **$/khách/SLO/error-budget**; chi phí trong trần **~$300/tuần**; đánh đổi có con số, không "cho chắc".
```
Điểm: [1] [2] [3] [4] [5]
Dẫn chứng bắt buộc: ______________________________________________________________
```

### Chiều 4 — AI-Eng [AIO] / Reliability [CDO]  *(W1: VỪA — nhận diện & kế hoạch)*
- **CDO:** nhận diện đúng gap reliability đúng altitude (probe, ≥2 replica checkout path, state bền valkey/postgres/kafka), có kế hoạch.
- **AIO:** đánh giá tầng AI (llm đang **mock**, thiếu eval/guardrail/fallback), kế hoạch cắm model thật + eval.
```
Điểm: [1] [2] [3] [4] [5]
Dẫn chứng bắt buộc: ______________________________________________________________
```

### Chiều 5 — Communication  *(W1: MẠNH — qua PRR + QnA)*
Trình bày rõ; **giữ lập luận có số khi bị 3 vai phản biện (CFO/SRE/PM)**; điều chỉnh hợp lý khi bị vặn; không phòng thủ cảm tính.
```
Điểm: [1] [2] [3] [4] [5]
Dẫn chứng bắt buộc: ______________________________________________________________
```

### Chiều 6 — Leadership / Ownership  *(W1: VỪA)*
Chủ động nhận DRI/own mục backlog; handoff on-call rõ; kéo nhóm ở takeover; theo tới cùng.
```
Điểm: [1] [2] [3] [4] [5]
Dẫn chứng bắt buộc: ______________________________________________________________
```

---

## 5. PRR (T6 W1) — Individual defense notes

Hỏi thẳng HV walk-through **chính mục họ own**. Ghi để lấy context cho scorecard + bắt free-rider.

```
Mục HV bảo vệ: ______________________________________________
Walk-through được không?      [ ] Rõ, làm chủ  [ ] Lúng túng  [ ] Không giải thích được
Chịu phản biện (vai vặn: ___): ______________________________________________
Có số liệu hậu thuẫn?          [ ] Có  [ ] Định tính  [ ] Không
```

---

## 6. Cờ (flag) — bắt buộc ghi nếu có

```
[ ] Inflated completion  — khai Done nhưng repo/live không có bằng chứng.  Chi tiết: ________
[ ] Single-contributor   — 1 người làm hết, HV này không walk-through được.  Chi tiết: ________
[ ] Free-rider           — không quy được đóng góp nào về tên.  Chi tiết: ________
[ ] Verbal-only          — chỉ nói "em làm rồi", không dẫn chứng.  Chi tiết: ________
```

---

## 7. Chốt điểm W1

```
Chiều 1 Judgment ___  | Chiều 2 Eng&Ops ___ | Chiều 3 Business ___
Chiều 4 AI/Reliab ___ | Chiều 5 Comm ___    | Chiều 6 Leadership ___

Tổng quan W1 (1-5): ___    Xu hướng cần theo dõi W2-3: ______________________________
Đã nộp rail /xbrain-score → outputs/forms/mentor_scorecards/  [ ]
Double-blind: đã chấm độc lập trước calibration  [ ]   Điểm lệch ≥1.0 cần re-discuss: [ ] chiều ___
```

> Nhắc: W1 = tín hiệu *takeover + judgment*. Xử lý sự cố thật, COE/postmortem, vận hành dưới ràng buộc → thu ở **W2-3**. Giữ scorecard này làm mốc so sánh tiến bộ.
