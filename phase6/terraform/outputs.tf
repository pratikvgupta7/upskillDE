output "bucket_name" {
  description = "S3 bucket name for data lake"
  value       = aws_s3_bucket.data_lake.bucket
}

output "bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.data_lake.arn
}

output "glue_database_name" {
  description = "Glue catalog database name"
  value       = aws_glue_catalog_database.taxi.name
}

output "pipeline_role_arn" {
  description = "IAM role ARN for pipeline services"
  value       = aws_iam_role.pipeline_role.arn
}

output "athena_workgroup" {
  description = "Athena workgroup name"
  value       = aws_athena_workgroup.taxi.name
}