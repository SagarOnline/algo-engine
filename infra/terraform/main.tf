provider "oci" {
  region = var.region
}

resource "oci_core_vcn" "vcn" {
  cidr_block     = local.network.vcn_cidr
  compartment_id = var.compartment_ocid
  display_name   = local.network.vcn_display_name
}

# Service Gateway for Oracle Services
resource "oci_core_service_gateway" "svc_gw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "service-gateway"
  services {
    service_id = data.oci_core_services.all_oci_services.services[0].id
  }
}

data "oci_core_services" "all_oci_services" {
  filter {
    name   = "name"
    values = ["all-*"]
  }
}

# Internet Gateway for public subnet
resource "oci_core_internet_gateway" "igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "internet-gateway"
  enabled        = true
}

# NAT Gateway for private subnet
resource "oci_core_nat_gateway" "natgw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "nat-gateway"
  block_traffic  = false
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

  route_rules {
    destination       = "all-services-in-oracle-services-network"
    destination_type  = "SERVICE_CIDR_BLOCK"
    network_entity_id = oci_core_service_gateway.svc_gw.id
  }
}

# Route Table for private subnet
resource "oci_core_route_table" "private_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "private-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_nat_gateway.natgw.id
  }

  route_rules {
    destination       = "all-services-in-oracle-services-network"
    destination_type  = "SERVICE_CIDR_BLOCK"
    network_entity_id = oci_core_service_gateway.svc_gw.id
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
resource "oci_core_network_security_group" "private_nsg" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "private-nsg"
}

resource "oci_core_network_security_group_security_rule" "private_nsg_ssh" {
  network_security_group_id = oci_core_network_security_group.private_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = local.network.vcn_cidr
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = 22
      max = 22
    }
  }
}

resource "oci_core_network_security_group_security_rule" "private_nsg_5000" {
  network_security_group_id = oci_core_network_security_group.private_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = local.network.vcn_cidr
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

# Private Subnet
resource "oci_core_subnet" "private" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.vcn.id
  cidr_block                 = local.network.private_subnet_cidr
  display_name               = "private-subnet"
  prohibit_public_ip_on_vnic = true
  route_table_id             = oci_core_route_table.private_rt.id
  security_list_ids          = null
  # nsg_ids is not supported for oci_core_subnet, use create_vnic_details.create_nsg_ids in oci_core_instance
}

# Compute Instance in Private Subnet
resource "oci_core_instance" "private_vm" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_ocid
  shape               = local.vm.shape

  shape_config {
    ocpus         = local.vm.ocpus
    memory_in_gbs = local.vm.memory_in_gbs
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.private.id
    assign_public_ip = false
    display_name     = "private-vm-vnic"
    nsg_ids          = [oci_core_network_security_group.private_nsg.id]
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
