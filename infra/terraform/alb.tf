resource "oci_core_network_security_group" "alb_nsg" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "alb-nsg"
}

resource "oci_core_network_security_group_security_rule" "alb_80" {
  network_security_group_id = oci_core_network_security_group.alb_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = 80
      max = 80
    }
  }
}

resource "oci_core_network_security_group_security_rule" "alb_443" {
  network_security_group_id = oci_core_network_security_group.alb_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = 443
      max = 443
    }
  }
}

resource "oci_network_load_balancer_network_load_balancer" "algo_nlb" {
  compartment_id             = var.compartment_ocid
  display_name               = local.vm.display_name
  subnet_id                  = oci_core_subnet.public.id
  is_private                 = false
  network_security_group_ids = [oci_core_network_security_group.alb_nsg.id]
}

resource "oci_network_load_balancer_backend_set" "algo_nlb_backend_set_http" {
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.algo_nlb.id
  name                     = "http"
  policy                   = "FIVE_TUPLE"
  health_checker {
    protocol = "TCP"
    port     = 8008
  }
}

resource "oci_network_load_balancer_backend_set" "algo_nlb_backend_set_https" {
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.algo_nlb.id
  name                     = "https"
  policy                   = "FIVE_TUPLE"
  health_checker {
    protocol = "TCP"
    port     = 443
  }
}

resource "oci_network_load_balancer_backend" "algo_nlb_backend_http" {
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.algo_nlb.id
  backend_set_name         = oci_network_load_balancer_backend_set.algo_nlb_backend_set_http.name
  ip_address               = oci_core_instance.algo_vm.private_ip
  port                     = 8008
  weight                   = 1
}

resource "oci_network_load_balancer_backend" "algo_nlb_backend_https" {
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.algo_nlb.id
  backend_set_name         = oci_network_load_balancer_backend_set.algo_nlb_backend_set_https.name
  ip_address               = oci_core_instance.algo_vm.private_ip
  port                     = 443
  weight                   = 1
}

resource "oci_network_load_balancer_listener" "algo_nlb_listener_http" {
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.algo_nlb.id
  name                     = "http"
  default_backend_set_name = oci_network_load_balancer_backend_set.algo_nlb_backend_set_http.name
  port                     = 80
  protocol                 = "TCP"
}

resource "oci_network_load_balancer_listener" "algo_nlb_listener_https" {
  network_load_balancer_id = oci_network_load_balancer_network_load_balancer.algo_nlb.id
  name                     = "https"
  default_backend_set_name = oci_network_load_balancer_backend_set.algo_nlb_backend_set_https.name
  port                     = 443
  protocol                 = "TCP"
}


