# W6 — Terraform: Xây nền tảng 3-tier an toàn (Bài tập cá nhân)

> Nộp bài cá nhân. Chấm tự động. 100 điểm.

Tuần này bạn học Infrastructure as Code với Terraform. Trước giờ nhóm bạn thao
tác trên AWS console; giờ bạn mô tả một phần của chính kiến trúc 3-tier đó
**bằng code**.

**Không có code mẫu (starter).** Bạn tự viết Terraform từ đầu — tự đặt cấu trúc
file, tự đặt tên resource, tùy ý dùng variable, local, `count`/`for_each`. Bộ
chấm **không tìm theo tên cụ thể**; nó kiểm tra *thực tế cấu hình của bạn tạo ra
cái gì*. Tuần này có **hai yêu cầu về cấu trúc** (vì đó chính là mục tiêu học):
tổ chức code thành ít nhất một **module**, và khai báo **remote state backend**
(chi tiết ở phần "Cần xây gì").

**Bạn KHÔNG deploy gì cả.** Việc chấm chạy trên kết quả `terraform plan`, nên
bạn không cần AWS account và không tốn một xu nào.

---

## Chuẩn bị

1. Cài [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.6
   (gõ `terraform version` để kiểm tra).
2. Tạo thư mục làm việc và viết Terraform trong các file `.tf` tùy ý — đặt tên,
   sắp xếp thế nào cũng được.

**Không có yêu cầu cấu trúc nào** — không bắt tên file, không bắt cấu hình
provider, không cố định tên resource. Bộ chấm đánh giá *cấu hình của bạn tạo ra
cái gì*, và khi chấm nó tự cấp provider offline, nên bạn không cần AWS account
hay credentials.

**Test ở máy (tùy chọn):** nếu muốn tự chạy `terraform plan` mà không có AWS
account, thêm các cờ sau vào khối `provider "aws"` để nó khỏi xác thực (đây đúng
là thứ bộ chấm tự làm cho bạn, nên có hay không cũng không ảnh hưởng điểm):

```hcl
provider "aws" {
  region                      = "ap-southeast-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
}
```

Vừa làm vừa kiểm tra:
```
terraform init
terraform validate
terraform plan        # chạy offline với các cờ ở trên
terraform fmt         # format code (có tính điểm)
```

**Về remote backend và test ở máy.** Một block `backend "s3" { ... }` thật sẽ
khiến `terraform init` gọi ra AWS và lỗi khi offline. Vì vậy trong lúc test
`plan` ở máy, **hãy comment block backend lại**, và **bật lại trước khi nộp**.
Bạn không mất gì cả: bộ chấm đọc yêu cầu backend **trực tiếp từ file của bạn (chấm
tĩnh)** và tự gỡ block đó khỏi bản sao của nó trước khi plan, nên nó không bao
giờ cản việc chấm.

**Self-check (nên chạy trước khi nộp):** dùng công cụ trong
[`student_check/`](student_check/README.md) để xác nhận đã có đủ resource:
```
python student_check/check.py đường-dẫn/tới/thư-mục-của-bạn
```
Nó chỉ kiểm tra resource có *tồn tại* hay chưa — bộ chấm của trainer còn kiểm tra
thêm các chi tiết bảo mật/network/nối-dây để tính điểm.

---

## Cần xây gì

Xây các thành phần sau. Giá trị **in đậm** là bị chấm; phần còn lại (tên, cấu
trúc, resource thêm) do bạn tự quyết.

### 1. Mạng (21 điểm)
- Một **VPC** với CIDR **`10.0.0.0/16`** và **`enable_dns_hostnames = true`**.
- Một **Internet Gateway**.
- **2 subnet public** (tự gán public IP) và **2 subnet private**, trải trên **ít
  nhất 2 Availability Zone**.
- Một route cho **`0.0.0.0/0`** đi qua Internet Gateway (dùng `aws_route` riêng
  hoặc route block inline — tùy bạn).

### 2. S3 bucket an toàn (17 điểm)
Một bucket có:
- **Versioning Enabled.**
- **Chặn truy cập public hoàn toàn** (cả 4 cờ block/restrict đều `true`).
- **Mã hóa server-side** (`AES256` hoặc `aws:kms`).

### 3. Security group tầng ứng dụng (20 điểm)
- Cho phép inbound **443** từ `0.0.0.0/0`.
- Cho phép inbound **80** từ `0.0.0.0/0`.
- **KHÔNG mở port 22 (SSH) ra `0.0.0.0/0`** — chấm riêng (9 điểm), là lỗi cấu
  hình phổ biến nhất trong thực tế. Bị phát hiện ở mọi dạng (rule inline hay
  resource rule riêng).

### 4. EC2 instance (11 điểm)
- Một EC2 với **`instance_type = "t3.micro"` lấy từ một variable** (không
  hardcode trực tiếp).
- Đặt trong **một subnet private** của bạn.
- **Gắn security group** tầng ứng dụng.
- Có **tag `Name`**.
- (Dùng giá trị `ami_id` cho sẵn bên dưới — không có tra cứu AMI thực.)

### 5. IAM (8 điểm)
- Một **IAM role** có trust policy cho phép **`ec2.amazonaws.com`** assume.
- Một **instance profile** bọc role đó.

### 6. Modules (8 điểm)
- Tổ chức code thành **ít nhất một module** chứa một phần thực sự của hệ thống
  (**≥ 3 resource**) — không phải module bọc cho có.
- Bạn có thể tách, ví dụ, phần mạng thành module riêng rồi cho tầng compute dùng
  output của nó. Bộ chấm **lần được tham chiếu xuyên qua ranh giới module**, nên
  các kiểm tra nối-dây (ví dụ "EC2 nằm trong subnet private") vẫn hoạt động dù
  subnet đến từ module gốc hay từ module con.

### 7. Remote state (7 điểm)
- Khai báo **S3 backend** có **state locking** và **mã hóa**:
  ```hcl
  terraform {
    backend "s3" {
      bucket         = "your-state-bucket"
      key            = "w6/terraform.tfstate"
      region         = "ap-southeast-1"
      dynamodb_table = "your-lock-table"   # hoặc: use_lockfile = true
      encrypt        = true
    }
  }
  ```
- Phần này chấm **tĩnh từ file của bạn** (bucket/table không cần tồn tại thật).
  Nhớ comment nó lại khi test `plan` ở máy — xem phần Chuẩn bị.

### Chất lượng code (8 điểm)
- **`terraform fmt`** sạch (3 điểm).
- Khai báo đủ các **tên output** sau (5 điểm): `vpc_id`, `public_subnet_ids`,
  `private_subnet_ids`, `bucket_name`, `security_group_id`, `instance_id`,
  `iam_role_arn`.

### Giá trị cố định phải dùng
- Region: `ap-southeast-1`
- VPC CIDR: `10.0.0.0/16`
- Instance type: `t3.micro` (qua một variable)
- AMI: `ami-0abcdef1234567890` (giá trị placeholder — dùng nguyên như vậy)

---

## Lên hạng Distinction — phần nâng cao (tùy chọn, +40)

100 điểm ở trên là để *đạt yêu cầu*. Ngoài ra có một band **Nâng cao** riêng (40
điểm) thưởng cho việc làm theo cách một kỹ sư cloud thực thụ. Bạn **không** cần
phần này để đạt, nhưng đây là cách phân loại bài giỏi. Mỗi mục tùy chọn và độc lập:

- **IAM least privilege** (8) — policy quyền của bạn giới hạn vào action và ARN cụ
  thể; không `Action: "*"`, không `Resource: "*"`, không gắn managed policy rộng
  như `AdministratorAccess`.
- **Tham số hóa** (6) — VPC CIDR *và* instance type đều lấy từ variable, không
  hardcode.
- **Bật IMDSv2** (5) — EC2 đặt `metadata_options { http_tokens = "required" }`.
- **Mã hóa volume** (5) — root volume của instance được mã hóa.
- **Hardening S3** (5) — bucket policy (ví dụ chặn truy cập không TLS) hoặc
  lifecycle configuration.
- **Mã hóa KMS** (5) — bucket dùng `aws:kms` (một KMS key) thay vì `AES256`.
- **VPC Flow Logs** (3) — một `aws_flow_log` trên VPC.
- **Tagging nhất quán** (3) — mọi VPC, subnet, security group, instance và bucket
  đều có tag.

Kết quả báo dạng **Core /100 + Advanced /40** kèm hạng: **Distinction** (core 100
và đa số phần nâng cao), **Merit**, **Pass**, hoặc **Needs work**.

---

## Nộp gì

Nộp các file **`.tf`** (và `.tfvars` nếu có). **Không** nộp `.terraform/`,
`tfplan.bin`, hay file state.
