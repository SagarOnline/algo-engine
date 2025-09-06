resource "oci_core_network_security_group_security_rule" "vm_algo_api" {
  network_security_group_id = oci_core_network_security_group.vm_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = local.algo.api_port
      max = local.algo.api_port
    }
  }
}

resource "oci_core_network_security_group_security_rule" "vm_algo_ui" {
  network_security_group_id = oci_core_network_security_group.vm_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = local.algo.ui_port
      max = local.algo.ui_port
    }
  }
}

resource "null_resource" "algo_api_setup" {
  depends_on = [null_resource.wait_for_ssh]
  triggers = {
    scripts_hash = sha1(join("", [
      for f in fileset("${path.module}/scripts", "**") :
      filesha1("${path.module}/scripts/${f}")
    ]))
  }

  provisioner "file" {
    content = templatefile("${path.module}/scripts/algo_vm_setup.sh.tpl", {
      git_repository = local.algo.git_repository,
      branch         = local.algo.branch
      algo_api_port  = local.algo.api_port
      algo_ui_port   = local.algo.ui_port
    })
    destination = "/tmp/algo_vm_setup.sh"
    connection {
      type        = "ssh"
      host        = oci_core_instance.algo_vm.public_ip
      user        = "opc"
      private_key = file("${path.module}/${var.vm_ssh_private_key}")
      timeout     = "2m"
    }
  }

  provisioner "file" {
    content = templatefile("${path.module}/scripts/algo-api.service.tpl", {
      algo_api_port = local.algo.api_port
    })
    destination = "/tmp/algo-api.service"
    connection {
      type        = "ssh"
      host        = oci_core_instance.algo_vm.public_ip
      user        = "opc"
      private_key = file("${path.module}/${var.vm_ssh_private_key}")
      timeout     = "2m"
    }
  }

  provisioner "file" {
    content = templatefile("${path.module}/scripts/algo-ui.conf.tpl", {
      algo_ui_port = local.algo.ui_port
    })
    destination = "/tmp/algo-ui.conf"
    connection {
      type        = "ssh"
      host        = oci_core_instance.algo_vm.public_ip
      user        = "opc"
      private_key = file("${path.module}/${var.vm_ssh_private_key}")
      timeout     = "2m"
    }
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/algo_vm_setup.sh",
      "dos2unix /tmp/algo_vm_setup.sh",
      "dos2unix /tmp/algo-api.service",
      "/tmp/algo_vm_setup.sh > /tmp/algo_vm_setup.log 2>&1"
    ]
    connection {
      type        = "ssh"
      host        = oci_core_instance.algo_vm.public_ip
      user        = "opc"
      private_key = file("${path.module}/${var.vm_ssh_private_key}")
      timeout     = "2m"
    }
  }
}
