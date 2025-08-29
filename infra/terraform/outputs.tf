output "vcn_cidr" {
  value = var.vcn_cidr
}

output "vcn_display_name" {
  value = var.vcn_display_name
}

output "vcn_id" {
  value = oci_core_vcn.vcn.id
}
