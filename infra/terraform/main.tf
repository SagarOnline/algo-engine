provider "oci" {
  region = var.region
}

resource "oci_core_vcn" "vcn" {
  cidr_block     = local.network.vcn_cidr
  compartment_id = var.compartment_ocid
  display_name   = local.network.vcn_display_name
}


# Internet Gateway for public subnet
resource "oci_core_internet_gateway" "igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "internet-gateway"
  enabled        = true
}


# Route Table for public subnet
resource "oci_core_route_table" "public_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.igw.id
  }
}



# Security List: allow all egress
resource "oci_core_security_list" "all_egress" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "allow-all-egress"

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

# Network Security Group: allow 22 and 5000 from VCN CIDR
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

resource "oci_core_network_security_group_security_rule" "vm_nsg_5000" {
  network_security_group_id = oci_core_network_security_group.vm_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = 5000
      max = 5000
    }
  }
}

# Public Subnet
resource "oci_core_subnet" "public" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.vcn.id
  cidr_block                 = local.network.public_subnet_cidr
  display_name               = "public-subnet"
  prohibit_public_ip_on_vnic = false
  route_table_id             = oci_core_route_table.public_rt.id
  security_list_ids          = null
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


# Run shell script on core_vm after creation
resource "null_resource" "core_vm_provision" {
  depends_on = [oci_core_instance.core_vm]
  triggers = {
    setup_script = filesha1("${path.module}/scripts/core_vm_setup.sh.tpl")
  }

  provisioner "file" {
    content     = templatefile("${path.module}/scripts/core_vm_setup.sh.tpl", {})
    destination = "/tmp/core_vm_setup.sh"
    connection {
      type        = "ssh"
      host        = oci_core_instance.core_vm.public_ip
      user        = "opc"
      private_key = file("${path.module}/${var.vm_ssh_private_key}")
      timeout     = "2m"
    }
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/core_vm_setup.sh",
      "dos2unix /tmp/core_vm_setup.sh",
      "/tmp/core_vm_setup.sh"
    ]
    connection {
      type        = "ssh"
      host        = oci_core_instance.core_vm.public_ip
      user        = "opc"
      private_key = file("${path.module}/${var.vm_ssh_private_key}")
      timeout     = "2m"
    }
  }
}
