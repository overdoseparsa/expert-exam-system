#!/bin/bash

BASE_DIR="modules"

folders=(
  "family_information"
  "contact_information"
  "military_service"
  "education"
  "work_experience"
  "skills"
  "language_skills"
  "training_courses"
  "jobs_information"
  "job_applications"
  "application_details"
)

files=(
  "models.py"
  "schemas.py"
  "services.py"
  "selectors.py"
  "router.py"
  "enums.py"
)

# ساخت base dir
mkdir -p "$BASE_DIR"

for folder in "${folders[@]}"; do
  folder_path="$BASE_DIR/$folder"
  mkdir -p "$folder_path"

  for file in "${files[@]}"; do
    file_path="$folder_path/$file"

    if [ ! -f "$file_path" ]; then
      touch "$file_path"
      echo "# $file for $folder" > "$file_path"
    fi
  done
done

echo "✅ Structure created successfully!"