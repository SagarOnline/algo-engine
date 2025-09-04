resource "oci_core_network_security_group_security_rule" "core_ui" {
  network_security_group_id = oci_core_network_security_group.vm_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = local.algo_ui.port
      max = local.algo_ui.port
    }
  }
}

resource "null_resource" "algo_ui_setup" {
  depends_on = [null_resource.wait_for_ssh]
  triggers = {
    setup_script = filesha1("${path.module}/scripts/algo_ui_setup.sh.tpl")
  }

  provisioner "file" {
    content = templatefile("${path.module}/scripts/algo_ui_setup.sh.tpl", {
      git_repository = local.algo_ui.git_repository,
      branch         = local.algo_ui.branch
      algo_ui_port   = local.algo_ui.port
    })
    destination = "/tmp/algo_ui_setup.sh"
    connection {
      type        = "ssh"
      host        = oci_core_instance.core_vm.public_ip
      user        = "opc"
      private_key = file("${path.module}/${var.vm_ssh_private_key}")
      timeout     = "2m"
    }
  }

  provisioner "file" {
    content = templatefile("${path.module}/scripts/algo-ui.conf.tpl", {
      algo_ui_port = local.algo_ui.port
    })
    destination = "/tmp/algo-ui.conf"
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
      "chmod +x /tmp/algo_ui_setup.sh",
      "dos2unix /tmp/algo_ui_setup.sh",
      "dos2unix /tmp/algo-ui.conf",
      "/tmp/algo_ui_setup.sh > /tmp/algo_ui_setup.log 2>&1"
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
