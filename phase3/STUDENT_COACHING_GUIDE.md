# Góp ý cho sinh viên khi được hỏi — Sổ tay coaching cho Mentor (Phase 3)

Tài liệu này giúp mentor **trả lời câu hỏi của HV một cách nhất quán** trong suốt 3 tuần. Vì Phase 3 chấm **judgment > code**, nguyên tắc là **coach bằng câu hỏi, không giải hộ**. Giải hộ = làm hỏng chính thứ đang được chấm và làm sai lệch điểm cá nhân.

---

## 0. Ba nguyên tắc trả lời

1. **Coach, đừng giải.** Trả câu hỏi bằng câu hỏi ngược để HV tự tìm ra. Không đưa backlog mẫu, không chỉ đích danh sự cố, không viết ADR hộ.
2. **Phân biệt FACT vs JUDGMENT.**
   - *Fact* (được phép làm rõ): mọi thứ đã có trong `onboarding/`, `RULES.md`, `GETTING_STARTED.md` — kiến trúc, SLO, trần ngân sách, luật chơi, cách build/deploy.
   - *Judgment* (KHÔNG được nói hộ): ưu tiên việc gì, đánh đổi ra sao, sự cố này xử thế nào — đây là thứ HV phải tự hình thành và bảo vệ.
3. **Ranh giới disqualify phải cảnh báo NGAY và RÕ** — đây là ngoại lệ: không coach lòng vòng, nói thẳng để cứu đội (xem §3).

> Câu thần chú khi bí: *"Em quy được việc này về rủi ro × tác động business không? Đo bằng số nào? Truy về ai (ADR)?"*

---

## 1. Bảng ranh giới "được nói / không được nói"

| Chủ đề | ✅ Được làm rõ (fact) | ❌ Không nói hộ (judgment) |
|---|---|---|
| Kiến trúc/luồng | service nào gọi service nào, port, dependency | chỗ nào "đáng sửa trước" |
| SLO | ngưỡng, cửa sổ đo, error budget là gì | có nên tiêu budget cho việc X không |
| Ngân sách | trần ~$300/tuần gồm gì, công cụ theo dõi | có nên bật Multi-AZ/managed không |
| Build/deploy | lệnh build→ECR→helm, sửa lỗi dựng | kiến trúc target nên thế nào |
| Sự cố | *"đây là hệ thống có sự cố bơm vào, hãy quan sát telemetry"* | sự cố nào đang bật, do flag nào |
| flagd | flagd là hạ tầng được bảo vệ, cấm đụng | — (chỉ cảnh báo, không có vùng xám) |
| Deliverable | format ADR/postmortem, hạn nộp | nội dung quyết định nên là gì |

---

## 2. Setup / Build / Deploy — câu hỏi kỹ thuật (được giúp thoải mái)

Đây là vùng **fact** — giúp HV vượt qua để vào phần được chấm. Không có điểm judgment ở việc dựng, nên đừng để HV kẹt.

- **"Image pull lỗi / CrashLoopBackOff?"** → chỉ `GETTING_STARTED.md` mục "Sự cố thường gặp": kiểm `default.image.repository` trỏ đúng ECR, `kubectl logs`, thiếu secret `llm-api-key`, dependency (postgres/valkey/kafka) chưa Ready.
- **"`helm dependency build` lỗi?"** → nhắc chạy đủ `helm repo add` (open-telemetry/grafana/prometheus/jaeger/opensearch).
- **"Nên build đường A hay B?"** → làm rõ fact: A (build-from-source) là kỹ năng CI được chấm, B chỉ để bootstrap. Gợi ý: *"Đường nào để lại dấu vết chứng minh em build được?"*
- **"flagd cứ mất kết nối sau mỗi deploy?"** → nhắc phải ghép lại `-f deploy/values-flagd-sync.yaml` mỗi lần `helm upgrade`.

---

## 3. flagd / Sự cố / Ranh giới DISQUALIFY — nói thẳng, không lòng vòng

Đây là ngoại lệ của "coach bằng câu hỏi". Nếu HV có ý định đụng cơ chế sự cố, **cảnh báo dứt khoát**.

- **"Bọn em tắt cái flag gây lỗi cho hết sự cố được không?"**
  → **KHÔNG.** Nói thẳng: tắt/né/re-point flagd hay gỡ hook đọc flag = **disqualify cả đội**. Sự cố là để **chịu được** (fallback/retry/containment), không phải để tắt. Rồi mới coach: *"Làm gì để hệ thống vẫn phục vụ khách khi lỗi này xảy ra?"*
- **"Đây là lỗi hệ thống hay sự cố BTC bơm?"**
  → Không nói đáp án. Coach phân biệt: *"Nó bật/tắt được từ ngoài không? Nó có trong đường flag không? Nếu là thiếu sót cấu hình thật thì sửa gốc; nếu là thứ bị bật lên thì làm hệ thống chịu được — em kiểm bằng cách nào?"*
- **"Bọn em refactor service để không đọc flag nữa cho gọn?"**
  → **Cảnh báo:** gỡ đường dây đọc flag = disqualify ngang re-point flagd. Muốn bền thì thêm fallback/retry, **không tháo đường dây đang có**. (Được thêm flag/feature mới của mình.)
- **"Sự cố đang xảy ra, mentor chỉ em fix với?"**
  → Không fix hộ. Coach: *"Telemetry đang nói gì (Grafana/Jaeger/OpenSearch)? Chặn ảnh hưởng tới khách trước hay tìm root-cause trước? Containment nào rẻ nhất bây giờ?"*

---

## 4. Ưu tiên / Backlog / PRR — vùng judgment, TUYỆT ĐỐI không giải hộ

- **"Bọn em nên làm gì trước?"**
  → Không liệt kê việc. Coach: *"Cái gì hỏng thì mất tiền/khách nhiều nhất? Luồng nào ra tiền (SLO nói gì)? Việc đó tốn bao nhiêu trong trần? Xếp theo rủi ro × business đi rồi mình phản biện."*
- **"Backlog này ổn chưa mentor?"**
  → Đừng duyệt hộ. Hỏi ngược theo 3 vai: *"CFO sẽ hỏi tốn bao nhiêu? SRE hỏi test chưa, sai thì sao? PM hỏi tuần này khách được gì? Em trả được 3 câu đó chưa?"*
- **"Bỏ việc này có bị trừ điểm không?"**
  → Làm rõ fact: **bỏ đúng việc tác động thấp là kỹ năng được chấm**. Điều bị trừ là bỏ mà không giải thích được, hoặc bỏ nhầm việc quan trọng.
- **"PRR cần chuẩn bị gì?"**
  → Chỉ `PITCH_GUIDE.md`: hiểu hệ thống + backlog xếp hạng + bảo vệ thứ tự + cố ý bỏ gì. Nhắc: chấm **tư duy, không phải slide đẹp**; bị vặn là bình thường, giữ lập luận có số.

---

## 5. SLO & Error budget

- **"SLO sắp vỡ, bọn em có bị trừ nặng không?"**
  → Fact + reframe: mục tiêu **không phải** "SLO không bao giờ vỡ" mà là **giữ ảnh hưởng khách nhỏ nhất + phục hồi nhanh**. Cách xử lý mới được chấm. Coach: *"Còn error budget không? Nếu cháy thì đóng băng thay đổi rủi ro, ổn định trước — em quyết thế nào?"*
- **"Đo SLO ở đâu?"**
  → Fact: Prometheus/Grafana, rolling 24h. Gợi ý dựng dashboard SLO sớm — *"không đo được thì không quản được."*

---

## 6. Ngân sách / Cost

- **"Bật Multi-AZ / lên RDS cho chắc nhé?"**
  → Không chốt hộ. Coach: *"Nó thêm bao nhiêu $/tuần? Trong ~$300 chịu nổi? Rủi ro nó chống là gì, khả năng xảy ra cao không? ROI đâu? Ghi ADR chưa?"* Nhắc: bật "cho chắc" mà vỡ ngân sách là quyết định **tồi**.
- **"Chi nhiều tài nguyên cho mạnh có được điểm cao không?"**
  → Fact: không. Được nhìn là **hiệu quả chi phí / đơn vị tải**, không phải chi nhiều.

---

## 7. Theo trụ (CDO) — coach đúng altitude, gợi hướng chứ không giải

- **Reliability:** *"Chỗ nào là single point of failure? Pod chết thì khách mất gì? Em kiểm chứng bằng cách nào (drain node thử)?"* (Không nói thẳng `replicas:1`.)
- **Performance:** *"Khi tải tăng gấp 5, cái gì gãy trước? Em có số tải trước/sau không? Scale bằng gì?"*
- **Security:** *"Có secret nào đang nằm plaintext không? Ai vào được cái gì? Least-privilege ở đâu chưa có?"*
- **Cost:** *"Tiền đang chảy vào đâu nhiều nhất (Cost Explorer)? Cắt chỗ nào không phá SLO?"*
- **Auditability:** *"Một thay đổi bất kỳ, em truy được về ai + khi nào không? Bằng gì?"*

Nguyên tắc: hỏi để HV **tự tìm ra lỗ**, chỉ xác nhận khi họ đã nêu đúng bằng chứng.

---

## 8. Tầng AI (AIO)

- **"llm trả lời được rồi, xong chưa?"**
  → Fact: `llm` mặc định là **mock**. Coach: *"Nó có gọi model thật chưa? Em chứng minh tóm tắt đúng bằng eval nào? Khi llm lỗi/chậm thì khách thấy gì?"*
- **"Trợ lý trả lời trôi chảy là được chưa?"**
  → Fact: **trôi chảy KHÔNG được tính điểm**. Được chấm: gọi đúng tool trong phạm vi, grounded không bịa, có **eval task-success**. Coach: *"Thử ép nó checkout/xoá giỏ xem nó có từ chối không? Hỏi câu review không có, nó nói 'không biết' hay bịa?"*
- **"Eval thế nào là đủ?"**
  → Fact: phải **tái tạo được** (script + data commit). Số không repro coi như chưa chứng minh. Không đưa bộ eval mẫu — để HV tự thiết kế.
- **"AIOps cần làm tới đâu?"**
  → Fact bar cao: chạy **liên tục** + xử lý được sự cố thật, không demo 1 lần; có safety check (dry-run/blast-radius) trước khi tự động xử lý. Cảnh báo: tự động can thiệp vào flagd = disqualify.

---

## 9. Deliverables (ADR / Postmortem / Ops Review)

- **"ADR viết sao?"** → Fact format: context → options → **trade-off có số** → quyết định → hệ quả/rollback → **ký tên**. Không viết nội dung hộ. Nhắc: ADR viết lấp sau khi làm sẽ lộ khi bị hỏi.
- **"Postmortem có cần đổ lỗi ai không?"** → Fact: **blameless**. Cần timeline + MTTD/MTTR + root cause + action item chống tái diễn. Coach: *"Đừng dừng ở 'do BTC bơm flag' — hệ thống lẽ ra chịu được bằng cách nào?"*
- **"Ops Review trình gì?"** → Fact: SLO (số thật), tiêu ngân sách vs trần, sự cố + MTTD/MTTR, backlog/directive đã đóng — dựa trên **số đo**, không định tính.

---

## 10. Câu hỏi về đánh giá / cá nhân

- **"Điểm tính theo nhóm hay cá nhân?"**
  → Fact: có **điểm cá nhân** (mentor chấm scorecard 6 chiều, double-blind) + điểm nhóm/TF (panel). Nhắc: mọi điểm cần **dẫn chứng quy về tên** — ADR ký tên, ca on-call, walk-through được ở QnA.
- **"Làm sao để nổi bật?"**
  → Coach thẳng thắn: *"Quy được đóng góp về tên em không? Em walk-through được quyết định của mình khi bị hỏi thẳng không? Có số before/after không?"* Không hứa điểm.
- **"Em khai Done rồi mà?"**
  → Fact cứng: **không tính verbal claim**. Chỉ chấm khi có bằng chứng repo/live. Nhẹ nhàng yêu cầu chỉ ra commit/`kubectl`/dashboard.
- **"Cả nhóm làm chung, sao tách được của em?"**
  → Coach: *"Phần nào là quyết định của em? Ký ADR/COE, cầm ca on-call, own mục backlog — đó là cách em để lại dấu vết cá nhân."*

---

## 11. Khi nào KHÔNG trả lời (đẩy về tự quyết)

Nói thẳng "đây là phần các em phải tự quyết và bảo vệ" khi HV hỏi:
- Nên ưu tiên việc nào / bỏ việc nào.
- Sự cố đang bật là gì, do flag nào.
- Kiến trúc target "đúng" là gì.
- Đánh đổi cost/reliability nên chọn bên nào.
- Nội dung ADR/quyết định nên viết gì.

> Với những câu này, giá trị của mentor là **đặt câu hỏi sắc**, không phải đưa đáp án. Đáp án HV tự bảo vệ được ở PRR/Readout mới là thứ tính điểm.
