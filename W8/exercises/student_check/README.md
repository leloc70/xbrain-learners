# Self-check (students)

A quick way to confirm your Terraform contains all the resources the assignment
asks for, **before you submit**.

## Run it

From the assignment folder (Terraform ≥ 1.6 must be installed):

```
python student_check/check.py path/to/your/terraform/folder
```

or, if you are already inside your folder:

```
python /path/to/check.py
```

You do **not** need an AWS account or credentials — the script copies your files
to a temp folder, adds an offline provider, runs `terraform plan`, and reports
what your configuration would create.

## What it checks (and what it doesn't)

It only checks **presence**: that each required resource type exists (VPC, subnets,
S3 bucket, security group, EC2, IAM role, etc.) and that the required outputs are
declared.

It does **not** check the details that earn points — security rules (e.g. SSH not
open to the world), private-subnet placement, encryption settings, routing
correctness, and so on. The trainer's grader checks all of those.

So: `All required resources and outputs are present.` means your skeleton is
complete — keep reading the assignment to make sure each resource is configured
correctly.
