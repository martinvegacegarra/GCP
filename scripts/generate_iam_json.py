import json
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_iam_policy(project_id):
    try:
        result = subprocess.run(
            ['gcloud', 'projects', 'get-iam-policy', project_id, '--format=json'],
            capture_output=True, text=True, check=True
        )
        return project_id, json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving IAM policy for project {project_id}: {e}")
        return project_id, None

def save_user_to_file(user_info, output_dir):
    member = user_info["member"].replace(":", "_").replace("@", "_").replace(".", "_")
    file_path = os.path.join(output_dir, f"{member}.json")
    
    with open(file_path, 'w') as f:
        json.dump(user_info, f, indent=4)

def process_projects(project_file, output_dir):
    with open(project_file, 'r') as f:
        projects = [line.strip() for line in f]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_project = {executor.submit(get_iam_policy, project): project for project in projects}
        for future in as_completed(future_to_project):
            project = future_to_project[future]
            try:
                _, policy = future.result()
                if policy:
                    for binding in policy.get('bindings', []):
                        role = binding['role']
                        for member in binding.get('members', []):
                            user_info = {
                                "member": member,
                                "role": role,
                                "projectid": project
                            }
                            save_user_to_file(user_info, output_dir)
            except Exception as exc:
                print(f'Error processing project {project}: {exc}')

def main():
    project_file = 'projects.txt'
    output_dir = 'users_json'
    process_projects(project_file, output_dir)

if __name__ == '__main__':
    main()

