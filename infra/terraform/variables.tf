variable "region" {
  type        = string
  description = "OCI region (e.g. ap-mumbai-1)"
  default     = null
}

variable "compartment_ocid" {
  type        = string
  description = "Compartment OCID where the VCN will be created"
}
