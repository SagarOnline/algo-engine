resource "oci_core_network_security_group_security_rule" "vm_nsg_api" {
  network_security_group_id = oci_core_network_security_group.vm_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = local.core_api.port
      max = local.core_api.port
    }
  }
}


# Run shell script on core_vm after creation
resource "null_resource" "core_api_setup" {
  depends_on = [oci_core_instance.core_vm]
  triggers = {
    setup_script = filesha1("${path.module}/scripts/core_vm_setup.sh.tpl")
  }

  provisioner "file" {
    content = templatefile("${path.module}/scripts/core_vm_setup.sh.tpl", {
      git_repository = local.core_api.git_repository,
      branch         = local.core_api.branch
      core_api_port  = local.core_api.port
    })
    destination = "/tmp/core_vm_setup.sh"
    connection {
      type        = "ssh"
      host        = oci_core_instance.core_vm.public_ip
      user        = "opc"
      private_key = file("${path.module}/${var.vm_ssh_private_key}")
      timeout     = "2m"
    }
  }

  provisioner "file" {
    content = templatefile("${path.module}/scripts/algo-core.service.tpl", {
      core_api_port = local.core_api.port
    })
    destination = "/tmp/algo-core.service"
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
      "dos2unix /tmp/algo-core.service",
      "/tmp/core_vm_setup.sh > /tmp/core_vm_setup.log 2>&1"
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
