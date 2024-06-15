import os
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

def check_file_exists(kubeconfig_path):
    if not os.path.exists(kubeconfig_path):
        return False, f"File not found: {kubeconfig_path}"
    return True, None

def check_yaml_format(kubeconfig_path):
    try:
        with open(kubeconfig_path, 'r') as stream:
            yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        return False, f"Invalid YAML format: {exc}"
    return True, None

def check_kubeconfig_content(kubeconfig_path):
    try:
        config.load_kube_config(kubeconfig_path)
    except config.ConfigException as exc:
        return False, f"Kubeconfig content is invalid: {exc}"
    return True, None

def check_cluster_connection():
    try:
        v1 = client.CoreV1Api()
        v1.list_namespace()
    except ApiException as e:
        if e.status == 401:
            return False, "Authentication failed. Check your credentials."
        elif e.status == 403:
            return False, "Access forbidden. Check your permissions."
        elif e.status == 404:
            return False, "Cluster not found. Check the server URL."
        else:
            return False, f"Failed to connect to the cluster: {e.reason}"
    return True, None

def validate_kubeconfig(kubeconfig_path):
    # Check if file exists
    is_valid, error_message = check_file_exists(kubeconfig_path)
    if not is_valid:
        return error_message

    # Check if YAML format is valid
    is_valid, error_message = check_yaml_format(kubeconfig_path)
    if not is_valid:
        return error_message

    # Check if kubeconfig content is valid
    is_valid, error_message = check_kubeconfig_content(kubeconfig_path)
    if not is_valid:
        return error_message

    # Check if able to connect to the cluster
    is_valid, error_message = check_cluster_connection()
    if not is_valid:
        return error_message

    return "Kubeconfig is valid and cluster connection is successful."

if __name__ == "__main__":
    # Replace with the path to your kubeconfig file
    kubeconfig_path = os.path.expanduser("~/.kube/config")
    validation_result = validate_kubeconfig(kubeconfig_path)
    print(validation_result)
