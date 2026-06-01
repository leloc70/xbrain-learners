# W6 — Terraform: Build a Secure 3-Tier Foundation (Individual Assignment)

> Individual submission. Auto-graded. 100 points.

This week you have been learning Infrastructure as Code with Terraform. So far
your team has clicked through the AWS console; now you describe a slice of that
same 3-tier architecture **as code**.

There is **no starter code**. You write the Terraform yourself, from scratch —
your own file layout, your own resource names, your own use of variables,
locals, and `count`/`for_each`. The grader does not look for specific names; it
inspects *what your configuration actually builds*. Two pieces of **structure**
*are* required this week, because they are the learning goals: organising your
code into at least one **module**, and declaring a **remote state backend**
(details under "What to build").

**You never deploy anything.** Grading runs against `terraform plan` output, so
you do not need an AWS account and you will not spend a cent.

---

## Setup

1. Install [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.6
   (`terraform version` to check).
2. Create a working folder and write your Terraform in any `.tf` files, named
   and organised however you like.

There are **no structural requirements** — no required file names, no required
provider configuration, no fixed resource names. The grader evaluates what your
configuration *builds*, and it supplies its own offline provider when grading,
so you do not need an AWS account or credentials.

**Testing locally (optional):** if you want to run `terraform plan` yourself
without an AWS account, add these flags to your `provider "aws"` block so it
doesn't try to authenticate (this is exactly what the grader does for you, so it
won't affect your grade either way):

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

Check your work as you go:
```
terraform init
terraform validate
terraform plan        # offline, with the flags above
terraform fmt         # format your code (a graded item)
```

**About the remote backend and local testing.** A real `backend "s3" { ... }`
block makes `terraform init` reach out to AWS, which fails offline. So while you
test `plan` locally, **comment out your backend block**, and **re-enable it
before you submit**. You don't lose anything: the grader reads the backend
requirement *statically from your files* and strips the block from its own copy
before planning, so it never blocks grading.

**Self-check (recommended before submitting):** run the helper in
[`student_check/`](student_check/README.md) to confirm you have all the required
resources:
```
python student_check/check.py path/to/your/folder
```
It only checks that the resources *exist* — the trainer's grader additionally
checks the security/networking/wiring details that earn points.

---

## What to build

Build the following. Exact values that are graded are shown in **bold**;
everything else (names, structure, extra resources) is your choice.

### 1. Networking (21 pts)
- A **VPC** with CIDR **`10.0.0.0/16`** and **`enable_dns_hostnames = true`**.
- An **Internet Gateway**.
- **2 public** subnets (auto-assign public IP) and **2 private** subnets,
  spread across **at least 2 Availability Zones**.
- A route for **`0.0.0.0/0`** through the Internet Gateway (separate `aws_route`
  or an inline route block — your choice).

### 2. Secure S3 bucket (17 pts)
A bucket with:
- **Versioning Enabled.**
- **Public access fully blocked** (all four block/restrict flags `true`).
- **Server-side encryption** (`AES256` or `aws:kms`).

### 3. Application security group (20 pts)
- Allow inbound **443** from `0.0.0.0/0`.
- Allow inbound **80** from `0.0.0.0/0`.
- **Do NOT open port 22 (SSH) to `0.0.0.0/0`** — this is graded explicitly
  (9 pts) and is the most common real-world misconfiguration. It is detected in
  any form (inline rule or separate rule resource).

### 4. EC2 instance (11 pts)
- An EC2 instance with **`instance_type = "t3.micro"` supplied via a variable**
  (not hardcoded inline).
- Placed in **one of your private subnets**.
- **Attached to your application security group.**
- Has a **`Name` tag**.
- (Use the provided `ami_id` value below — there is no live AMI lookup.)

### 5. IAM (8 pts)
- An **IAM role** whose trust policy allows **`ec2.amazonaws.com`** to assume it.
- An **instance profile** that wraps that role.

### 6. Modules (8 pts)
- Organise your code into **at least one module** that contains a real slice of
  the stack (**≥ 3 resources**) — not a token wrapper.
- You may split, for example, the network into its own module and have the
  compute consume its outputs. The grader **follows references across module
  boundaries**, so wiring checks (e.g. "the EC2 sits in a private subnet") still
  work whether your subnet comes from the root module or out of a child module.

### 7. Remote state (7 pts)
- Declare a remote **S3 backend** with **state locking** and **encryption**:
  ```hcl
  terraform {
    backend "s3" {
      bucket         = "your-state-bucket"
      key            = "w6/terraform.tfstate"
      region         = "ap-southeast-1"
      dynamodb_table = "your-lock-table"   # or: use_lockfile = true
      encrypt        = true
    }
  }
  ```
- This is graded **statically from your files** (the bucket/table need not
  exist). Remember to comment it out while testing `plan` locally — see Setup.

### Code quality (8 pts)
- **`terraform fmt`** is clean (3 pts).
- These **output names** are declared (5 pts): `vpc_id`, `public_subnet_ids`,
  `private_subnet_ids`, `bucket_name`, `security_group_id`, `instance_id`,
  `iam_role_arn`.

### Fixed values to use
- Region: `ap-southeast-1`
- VPC CIDR: `10.0.0.0/16`
- Instance type: `t3.micro` (via a variable)
- AMI: `ami-0abcdef1234567890` (a placeholder value — use it as-is)

---

## Going further — for a Distinction (advanced, optional, +40)

The 100 points above are for *meeting the requirements*. On top of that there is
a separate **Advanced** band (40 points) that rewards doing things the way a
cloud engineer would. You do **not** need any of these to pass, but they are how
strong submissions are distinguished. Each is optional and independent:

- **IAM least privilege** (8) — your IAM permission policy is scoped to specific
  actions and resource ARNs; no `Action: "*"`, no `Resource: "*"`, no broad
  managed policy like `AdministratorAccess`.
- **Parameterised** (6) — the VPC CIDR *and* the instance type both come from
  variables, not hardcoded literals.
- **IMDSv2 enforced** (5) — the EC2 instance sets
  `metadata_options { http_tokens = "required" }`.
- **Encrypted volume** (5) — the instance’s root volume is encrypted.
- **S3 hardening** (5) — a bucket policy (e.g. deny non-TLS access) or a
  lifecycle configuration on the bucket.
- **KMS encryption** (5) — the bucket uses `aws:kms` (a KMS key) rather than
  `AES256`.
- **VPC Flow Logs** (3) — an `aws_flow_log` on your VPC.
- **Consistent tagging** (3) — every VPC, subnet, security group, instance and
  bucket carries tags.

Your result is reported as **Core /100 + Advanced /40** and a tier:
**Distinction** (core 100 and most of advanced), **Merit**, **Pass**, or
**Needs work**.

---

## What to submit

Submit your **`.tf` files** (and any `.tfvars`). Do **not** submit `.terraform/`,
`tfplan.bin`, or any state files.

Your grade comes entirely from running `terraform plan` on your submission and
checking the criteria above — there is no hidden trick beyond what is listed
here. The full point breakdown is in [`GRADING.md`](GRADING.md).
