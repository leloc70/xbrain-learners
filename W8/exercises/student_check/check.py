#!/usr/bin/env python3
"""
Student self-check for the W6 Terraform assignment.

This is a LIGHT check: it only tells you whether your configuration contains the
resources the assignment asks for. It does NOT check the deeper requirements
(security rules, private-subnet placement, encryption settings, etc.) that the
trainer's grader checks. Passing this self-check means your skeleton is complete,
not that you will get full marks — read the assignment for the details that earn
points.

Usage:
    python check.py [path-to-your-terraform-folder]    # default: current folder

You do NOT need an AWS account or credentials. The script makes a temporary copy
of your files, adds an offline provider, runs `terraform plan`, and inspects what
your configuration would create.

Requires: Terraform >= 1.6 on your PATH. (No Python packages needed.)
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# Dropped into a copy of your folder so `terraform plan` runs without real AWS
# credentials. Merged into your own provider (or added if you have none).
OVERRIDE_TF = '''\
provider "aws" {
  region                      = "ap-southeast-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
}
'''

SKIP_DIRS = {".terraform", ".git", "__pycache__"}
SKIP_FILES = {"tfplan.bin", ".terraform.lock.hcl"}

# (label, [acceptable resource types], minimum count)
REQUIRED_RESOURCES = [
    ("VPC",                         ["aws_vpc"], 1),
    ("Internet gateway",            ["aws_internet_gateway"], 1),
    ("Subnets (need >= 4)",         ["aws_subnet"], 4),
    ("Routing (route or route table)", ["aws_route", "aws_route_table"], 1),
    ("S3 bucket",                   ["aws_s3_bucket"], 1),
    ("S3 versioning",               ["aws_s3_bucket_versioning"], 1),
    ("S3 public access block",      ["aws_s3_bucket_public_access_block"], 1),
    ("S3 encryption",               ["aws_s3_bucket_server_side_encryption_configuration"], 1),
    ("Security group",              ["aws_security_group"], 1),
    ("EC2 instance",                ["aws_instance"], 1),
    ("IAM role",                    ["aws_iam_role"], 1),
    ("Instance profile",            ["aws_iam_instance_profile"], 1),
]

REQUIRED_OUTPUTS = [
    "vpc_id", "public_subnet_ids", "private_subnet_ids",
    "bucket_name", "security_group_id", "instance_id", "iam_role_arn",
]


def strip_backend(text):
    """Remove `backend "..." { ... }` blocks (brace-matched) so the staged copy
    plans offline — a real S3 backend would make `terraform init` call AWS. Your
    own files are not touched."""
    out, i = [], 0
    while True:
        m = re.search(r'backend\s+"[^"]+"\s*\{', text[i:])
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:i + m.start()])
        k, depth = i + m.end() - 1, 0
        while k < len(text):
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        i = k + 1
    return "".join(out)


def stage(src):
    work = tempfile.mkdtemp(prefix="tfcheck_")
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel = os.path.relpath(root, src)
        dest = work if rel == "." else os.path.join(work, rel)
        os.makedirs(dest, exist_ok=True)
        for f in files:
            if f in SKIP_FILES:
                continue
            sp, dp = os.path.join(root, f), os.path.join(dest, f)
            if f.endswith(".tf"):
                with open(sp, encoding="utf-8") as fh:
                    text = fh.read()
                with open(dp, "w", encoding="utf-8") as fh:
                    fh.write(strip_backend(text))
            else:
                shutil.copy2(sp, dp)
    with open(os.path.join(work, "zz_check_override.tf"), "w", encoding="utf-8") as fh:
        fh.write(OVERRIDE_TF)
    return work


def has_module(root):
    """True if some child module declares >= 3 resources."""
    stack = list(root.get("child_modules", []))
    while stack:
        cm = stack.pop()
        if len(cm.get("resources", [])) >= 3:
            return True
        stack.extend(cm.get("child_modules", []))
    return False


def has_backend(src):
    """True if a `backend "s3"` block is declared in a root-level .tf file."""
    try:
        names = os.listdir(src)
    except OSError:
        return False
    for f in names:
        p = os.path.join(src, f)
        if f.endswith(".tf") and os.path.isfile(p):
            with open(p, encoding="utf-8") as fh:
                if re.search(r'backend\s+"s3"\s*\{', fh.read()):
                    return True
    return False


def run(args, cwd):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def walk_resources(module):
    for r in module.get("resources", []):
        yield r
    for c in module.get("child_modules", []):
        yield from walk_resources(c)


def main():
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    tf = shutil.which("terraform")
    if not tf:
        print("ERROR: terraform is not on your PATH. Install it first.")
        return 2

    print("Checking: %s\n" % src)
    work = stage(src)
    try:
        rc, out, err = run([tf, "init", "-input=false", "-no-color"], work)
        if rc != 0:
            print("terraform init failed:\n" + (err or out))
            return 1

        rc, out, err = run([tf, "validate", "-no-color"], work)
        if rc != 0:
            print("terraform validate failed (fix syntax/config errors first):\n" + (out or err))
            return 1

        rc, out, err = run([tf, "plan", "-input=false", "-refresh=false",
                            "-lock=false", "-out=tfplan.bin", "-no-color"], work)
        if rc != 0:
            print("terraform plan failed:\n" + (err or out))
            return 1

        rc, out, err = run([tf, "show", "-json", "tfplan.bin"], work)
        if rc != 0:
            print("terraform show failed:\n" + (err or out))
            return 1
        plan = json.loads(out)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    root = plan.get("planned_values", {}).get("root_module", {})
    resources = list(walk_resources(root))
    counts = {}
    for r in resources:
        counts[r.get("type")] = counts.get(r.get("type"), 0) + 1

    declared_outputs = set(plan.get("configuration", {})
                           .get("root_module", {}).get("outputs", {}).keys())

    all_ok = True
    print("Resources:")
    for label, types, minimum in REQUIRED_RESOURCES:
        have = sum(counts.get(t, 0) for t in types)
        ok = have >= minimum
        all_ok = all_ok and ok
        mark = "[ OK ]" if ok else "[MISS]"
        extra = "" if ok else "  (found %d, need %d)" % (have, minimum)
        print("  %s %s%s" % (mark, label, extra))

    print("\nOutputs:")
    for name in REQUIRED_OUTPUTS:
        ok = name in declared_outputs
        all_ok = all_ok and ok
        print("  %s %s" % ("[ OK ]" if ok else "[MISS]", name))

    print("\nStructure:")
    mod_ok = has_module(root)
    all_ok = all_ok and mod_ok
    print("  %s At least one module (>= 3 resources)" % ("[ OK ]" if mod_ok else "[MISS]"))
    backend_ok = has_backend(src)
    all_ok = all_ok and backend_ok
    print("  %s Remote backend declared (backend \"s3\")%s"
          % ("[ OK ]" if backend_ok else "[MISS]",
             "" if backend_ok else "  (graded statically; OK to comment out while testing)"))

    print("\n" + ("-" * 50))
    if all_ok:
        print("All required resources and outputs are present.")
        print("NOTE: this only checks presence. The trainer's grader also checks")
        print("security, networking and wiring details - see the assignment.")
        return 0
    else:
        print("Some items are missing (see [MISS] above). Keep going!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
