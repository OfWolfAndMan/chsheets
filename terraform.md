---
title: Terraform
summary: Terraform — init/plan/apply, state, modules, variables, and the OpenTofu fork
tags: [iac, terraform, opentofu, cloud]
tooling: [terraform, opentofu]
verified_on: 2026-11-10
verified_env: Terraform 1.15.9 — init/validate/plan/apply/state/destroy executed on a local example
status: verified
---

# Terraform

Verified with Terraform 1.15.9: the workflow below was executed end to end against a
local provider, so the commands are real even though the resources are not a cloud.

**Licence note.** Terraform has shipped under the Business Source Licence (BSL 1.1)
since v1.6 in August 2023. OpenTofu is the MPL-2.0 fork, governed by the Linux
Foundation; `tofu` accepts the same HCL and most of the same workflow. If you need an
OSI-approved licence, use OpenTofu. If you need the registry and the vendor's
commercial support, use Terraform. The commands below are identical except for the
binary name, which is why this sheet is written for `terraform` with a note at the end.

## The loop

```bash
terraform fmt -recursive          # canonical formatting
terraform init                    # download providers, initialise backend
terraform validate                # syntax and type checks, no API calls
terraform plan -out=tfplan        # show the change, save it for review
terraform apply tfplan            # apply exactly what was reviewed
terraform state list              # what Terraform believes it manages
terraform output                  # values exported by the configuration
terraform destroy                 # remove everything this state owns
```

`plan -out` plus `apply tfplan` is the difference between infrastructure as code and
infrastructure as a keystroke: what runs is the plan someone read.

## Project layout

```text
.
├── main.tf          # resources
├── variables.tf     # inputs, with types and defaults
├── outputs.tf       # values to export
├── versions.tf      # terraform and provider constraints
├── terraform.tfvars # environment values — never secrets
└── .terraform.lock.hcl   # provider checksums — commit this
```

Commit `.terraform.lock.hcl`; ignore `.terraform/` and `*.tfstate` when using a remote
backend.

## Configuration

```hcl
# versions.tf
terraform {
  required_version = ">= 1.6"

  required_providers {
    local = { source = "hashicorp/local", version = "~> 2.5" }
  }
}
```

```hcl
# variables.tf
variable "environment" {
  description = "deployment target"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging or prod"
  }
}

variable "content" {
  type      = string
  default   = "managed by terraform"
  sensitive = false
}
```

```hcl
# main.tf
locals {
  name = "example-${var.environment}"
}

resource "local_file" "config" {
  filename = "${path.module}/${local.name}.txt"
  content  = var.content
}
```

```hcl
# outputs.tf
output "config_path" {
  value       = local_file.config.filename
  description = "where the file was written"
}
```

```bash
terraform init
terraform validate
terraform plan -var 'environment=staging' -out=tfplan
terraform apply tfplan
terraform output -raw config_path
```

## Variables and precedence

```bash
terraform plan -var 'environment=prod'          # command line, highest precedence
export TF_VAR_environment=prod                  # environment
terraform plan -var-file=prod.tfvars            # a file
# terraform.tfvars is loaded automatically
```

Secrets do not belong in `.tfvars` files that are committed. Use `TF_VAR_*` from a
secret manager, or a provider that reads them at runtime. Mark a variable
`sensitive = true` and Terraform will redact it from plan output — that redaction is
cosmetic, the value is still in state.

## State

State is the mapping between configuration and real objects. It is the most valuable
and most dangerous file in the project.

```hcl
terraform {
  backend "s3" {
    bucket         = "example-tfstate"
    key            = "network/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

- Remote backend plus a lock table: two engineers cannot apply at once.
- Encrypt at rest; state contains values that were never meant to be public.
- Never edit state by hand. `terraform state mv`, `state rm` and `import` exist for
  the cases where editing feels necessary.

```bash
terraform state list
terraform state show local_file.config
terraform import local_file.config ./example-dev.txt
terraform state mv local_file.config local_file.renamed
```

## Drift and refresh

```bash
terraform plan -refresh-only       # what changed outside Terraform
terraform apply -refresh-only      # accept reality into state
terraform plan -detailed-exitcode  # 0 no change, 1 error, 2 changes pending
```

`-detailed-exitcode` is what makes `plan` usable in CI: exit 2 means "there is a diff",
which is a fact, not a failure.

## Modules

```hcl
module "network" {
  source  = "git::https://example.com/infra/modules/network.git?ref=v1.2.0"
  name    = "core"
  cidr    = "192.0.2.0/24"

  providers = {
    local = local
  }
}
```

Pin `ref` to a tag or commit. A module pointing at a branch is a configuration that
changes without a commit in your repository.

## Workspaces

```bash
terraform workspace list
terraform workspace new staging
terraform workspace select staging
```

Workspaces share one backend and one configuration with separate state. They suit
identical environments; they are a poor fit when environments differ materially — two
directories with their own state are easier to reason about.

## Formatting and validation in CI

```bash
terraform fmt -check -recursive    # fails if anything is unformatted
terraform validate                 # after init
terraform plan -detailed-exitcode -out=tfplan
```

`validate` without `init` fails on unresolved providers. Run `init -backend=false` in
CI when you only want syntax checking and no state access.

## OpenTofu

```bash
tofu init
tofu plan
tofu apply
```

OpenTofu 1.x keeps the HCL, the provider registry protocol and the state format. The
differences that matter: MPL-2.0 licence, state encryption as a built-in feature
(`encryption` block in the backend configuration), and a registry that mirrors the
public one. Migration in practice is `tofu init` against the existing state, after
taking a backup.

## Traps worth remembering

- `terraform apply` without a saved plan applies whatever was recomputed — not what
  you reviewed.
- State is not a backup. Losing it means importing every resource by hand.
- `count` on a list reindexes when an element is removed in the middle; `for_each` with
  a map is stable and should be the default.
- `sensitive = true` redacts output, not state.
- Deleting a resource block does not delete the resource unless you apply — the plan
  will say so, if anyone reads it.
