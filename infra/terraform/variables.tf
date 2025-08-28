variable "tenancy_ocid" {
  type        = string
  description = "OCI Tenancy OCID"
  default     = null
}

variable "user_ocid" {
  type        = string
  description = "OCI User OCID"
  default     = null
}

variable "fingerprint" {
  type        = string
  description = "OCI API Key fingerprint"
  default     = null
}

variable "private_key_path" {
  type        = string
  description = "Path to OCI API private key PEM"
  default     = "~/.oci/oci_api_key.pem"
}

variable "region" {
  type        = string
  description = "OCI region (e.g. ap-mumbai-1)"
  default     = null
}

variable "compartment_ocid" {
  type        = string
  description = "Compartment OCID where the VCN will be created"
}

variable "vcn_cidr" {
  type        = string
  description = "CIDR block for the VCN"
  default     = "10.0.0.0/16"
}

variable "vcn_display_name" {
  type        = string
  description = "VCN display name"
  default     = "algo-core-vcn"
}

variable "vcn_dns_label" {
  type        = string
  description = "DNS label (must be unique within compartment/tenancy constraints)"
  default     = "algocore"
}
