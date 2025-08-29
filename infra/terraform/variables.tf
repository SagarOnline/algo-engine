variable "region" {
  type        = string
  description = "OCI region (e.g. ap-mumbai-1)"
  default     = null
}

variable "compartment_ocid" {
  type        = string
  description = "Compartment OCID where the VCN will be created"
}

variable "vm_ssh_private_key" {
  description = "SSH private key for connecting to core_vm (should be set from GitHub secret VM_SSH_PRIVATE_KEY)"
  type        = string
  sensitive   = true
}
