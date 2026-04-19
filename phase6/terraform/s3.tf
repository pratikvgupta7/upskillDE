# main data lake bucket
resource "aws_s3_bucket" "data_lake" {
  bucket = var.bucket_name
}

# block all public access — data lake should never be public
resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# enable versioning — protects against accidental deletion
resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

# lifecycle policy — move old data to cheaper storage
resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    id     = "archive_old_data"
    status = "Enabled"

    filter {}    # add this — applies rule to all objects

    transition {
      days          = 90
      storage_class = "STANDARD_IA"  # infrequent access — cheaper
    }

    transition {
      days          = 365
      storage_class = "GLACIER"  # archival — very cheap
    }
  }
}

# folder structure — create logical prefixes
resource "aws_s3_object" "folders" {
  for_each = toset([
    "raw/",
    "clean/",
    "warehouse/",
    "streaming/",
  ])

  bucket  = aws_s3_bucket.data_lake.id
  key     = each.value
  content = ""
}