terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 5.38.0"
    }
  }
}

terraform {
  # Remote state in OCI Object Storage (values are supplied via -backend-config in the workflow)
  backend "s3" {
    bucket                      = "infra-state"
    region                      = "ap-mumbai-1"
    key                         = "algo-core.tfstate"
    skip_region_validation      = true
    skip_credentials_validation = true
    skip_requesting_account_id  = true
    use_path_style              = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
    endpoint                    = "https://bmyojs6ko6dg.compat.objectstorage.ap-mumbai-1.oraclecloud.com"
  }
}