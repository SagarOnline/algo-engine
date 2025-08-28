terraform {
  required_version = ">= 1.4.0"

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 5.38.0"
    }
  }

  # Remote state in OCI Object Storage (values are supplied via -backend-config in the workflow)
  backend "oci" {}
}

provider "oci" {
  # Provider reads these from environment variables:
  #   OCI_TENANCY_OCID, OCI_USER_OCID, OCI_FINGERPRINT, OCI_REGION
  #   plus private_key_path is used only for backend; provider can use resource principal or below envs
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

resource "oci_core_vcn" "vcn" {
  cidr_block     = var.vcn_cidr
  compartment_id = var.compartment_ocid
  display_name   = var.vcn_display_name
  dns_label      = var.vcn_dns_label
}

output "vcn_id" {
  value = oci_core_vcn.vcn.id
}
