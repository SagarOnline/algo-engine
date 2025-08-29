locals {
  application_name = "algo-core"
  network = {
    vcn_display_name    = "${local.application_name}"
    vcn_cidr            = "10.0.0.0/16"
    private_subnet_cidr = "10.0.2.0/24"
    public_subnet_cidr  = "10.0.1.0/24"
  }

  vm = {
    display_name    = "${local.application_name}"
    shape           = "VM.Standard.A1.Flex"
    ocpus           = 2
    memory_in_gbs   = 4
    boot_volume_gbs = 50
    ssh_public_key  = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCroI9IxwO/e7zMemyuBr2xUyTW7+mYy6brQiqRXpxh6WfKDI5XsRsb9XQRjwszScfd7bph5FdnFPP6gHUV7uB6nZ0rRMMcaUtyS2dKAqqhtxl+uHL3vdmbrJn+EkTDMCjkg5ODBGSrFV4s7jpBZGGT3B43qAVsuhGKoZmrjMNRIZPoptOrSD7nQbS6IUENaO3BWAPoL5ehyD6vTLi+B5lfkv03Fdq+wU/Yvb8WGl+mEZArGiVM4hcRgIGLx8hKm+ZIiXFxRZm+RhNT3x5KtjS8x3S3MWWbjpu+gesf0TDYRyhZQTQONNUNj5G3TIfImXVRZESym/lRrmalAtuPRAEPFFRNCPEzbR3pmfb2UU6/uQ4be+rcigqmOXTZRgy7meQPOoaVlbh5hcM3hy1HjUQlNksT5MWdt6+pQbld/JcBiisoy0+wesOYehC4DIVbeuS6vdbtQIFCWwgr7tApI/EYEOK5bCCFkDoYaNOXG1kpR+2khAdUISRDLMC9QNlDAeJHu/l1ekYoqVivQALe63bRqbyzq3t+kcpwwqC1qeprVauM0Ky4PLQ3uBtiGR1Wvvw4c4yWeUMkBqiOV7WiMTBX+UZSPa65rMea1DgSngj631obYc/jsL+BysCH8p3OfIlVxiVZPJhsJIu67DJtrnHmDLsH6UTcUhLibGGWsmJijw== chopade.sagar@gmail.com"
  }
  core_api = {
    git_repository = "https://github.com/SagarOnline/algo-engine.git"
    branch         = "main"
    port           = 5000
  }
}