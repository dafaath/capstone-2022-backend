locals {
  only_in_production_mapping = {
    test       = 0
    production = 1
  }
  only_in_production = local.only_in_production_mapping[terraform.workspace]
}

provider "google" {
  credentials = file(format("%s/../service-account-deploy.json", path.cwd))

  project = var.project_id
  region  = var.region
  zone    = var.zone
}

data "google_project" "current" {}

# Enable API Services
resource "google_project_service" "iam" {
  service = "iam.googleapis.com"
}

resource "google_project_service" "appengine" {
  service = "appengine.googleapis.com"
}

resource "google_project_service" "cloudsql" {
  count   = local.only_in_production
  service = "sqladmin.googleapis.com"
}

resource "google_project_service" "firestore" {
  service = "firestore.googleapis.com"
}

resource "google_project_service" "translate" {
  service = "translate.googleapis.com"
}


resource "google_compute_network" "backend" {
  count                   = local.only_in_production
  name                    = "backend"
  description             = "The backend network for REST API and Database"
  auto_create_subnetworks = true
}

resource "google_service_account" "app" {
  account_id   = var.service_account_name
  display_name = "Application Services Account"
}

resource "google_project_iam_member" "member-role" {
  for_each = toset([
    "roles/cloudtranslate.editor",
    "roles/datastore.owner",
    "roles/firestore.serviceAgent",
    "roles/storage.admin"
  ])
  role    = each.key
  member  = "serviceAccount:${google_service_account.app.email}"
  project = data.google_project.current.project_id
}

resource "google_app_engine_application" "app" {
  project       = data.google_project.current.project_id
  location_id   = var.region
  database_type = "CLOUD_FIRESTORE"
}

resource "google_storage_bucket" "photo_profile" {
  name                        = var.photo_profile_bucket
  location                    = var.region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_iam_member" "public" {
  bucket = google_storage_bucket.photo_profile.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_sql_database_instance" "main" {
  count            = local.only_in_production
  name             = "main-database"
  database_version = "POSTGRES_13"

  settings {
    tier = "db-custom-1-3840"
  }
}

resource "google_sql_database" "prod_db" {
  count    = local.only_in_production
  name     = "emodiary"
  instance = google_sql_database_instance.main[0].name
}


resource "google_sql_database" "test_db" {
  count    = local.only_in_production
  name     = "test_emodiary"
  instance = google_sql_database_instance.main[0].name
}

resource "google_firestore_index" "article" {
  collection = "articles"

  fields {
    field_path = "emotion"
    order      = "ASCENDING"
  }

  fields {
    field_path = "position"
    order      = "ASCENDING"
  }

}

resource "google_firestore_index" "diary" {
  collection = "diary"

  fields {
    field_path = "user_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "time_created"
    order      = "DESCENDING"
  }

}
