data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_ocid
}

data "oci_core_images" "oracle_linux_8" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Oracle Linux"
  operating_system_version = "8"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

# Compute Instance in Public Subnet
resource "oci_core_instance" "core_vm" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_ocid
  shape               = local.vm.shape

  shape_config {
    ocpus         = local.vm.ocpus
    memory_in_gbs = local.vm.memory_in_gbs
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public.id
    assign_public_ip = true
    display_name     = "public-vm-vnic"
    nsg_ids          = [oci_core_network_security_group.vm_nsg.id]
  }

  source_details {
    source_type             = "image"
    source_id               = data.oci_core_images.oracle_linux_8.images[0].id
    boot_volume_size_in_gbs = local.vm.boot_volume_gbs
  }

  metadata = {
    ssh_authorized_keys = local.vm.ssh_public_key
  }
}

# Network Security Group: allow 22 and api port from VCN CIDR
resource "oci_core_network_security_group" "vm_nsg" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "vm-nsg"
}

resource "oci_core_network_security_group_security_rule" "vm_nsg_ssh" {
  network_security_group_id = oci_core_network_security_group.vm_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = 22
      max = 22
    }
  }
}