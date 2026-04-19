# Glue catalog database — replaces your local REST catalog
resource "aws_glue_catalog_database" "taxi" {
  name        = "taxi"
  description = "NYC Yellow Taxi data — Iceberg tables"
}

# IAM role for Glue and Athena to access S3
resource "aws_iam_role" "pipeline_role" {
  name = "${var.project_name}-pipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = [
            "glue.amazonaws.com",
            "athena.amazonaws.com"
          ]
        }
      }
    ]
  })
}

# attach S3 access policy to the role
resource "aws_iam_role_policy" "pipeline_s3_access" {
  name = "${var.project_name}-s3-access"
  role = aws_iam_role.pipeline_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

# attach Glue service policy
resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.pipeline_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Athena workgroup — where queries run and results are stored
resource "aws_athena_workgroup" "taxi" {
  name = "${var.project_name}-workgroup"

  configuration {
    result_configuration {
      output_location = "s3://${aws_s3_bucket.data_lake.bucket}/athena-results/"
    }
  }
}

resource "aws_glue_crawler" "clean_data" {
  name          = "${var.project_name}-taxi-crawler"
  role          = aws_iam_role.pipeline_role.arn
  database_name = aws_glue_catalog_database.taxi.name

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/clean/"
  }

  schedule = "cron(0 6 * * ? *)"  # run daily at 6am

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  tags = {
    Project = "upskillDE"
  }
}