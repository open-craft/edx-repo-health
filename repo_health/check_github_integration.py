"""
Checks repository is on github actions workflow and tests are enabled.
"""
import json
import logging
import re

import requests
from pytest_repo_health import add_key_to_metadata

logger = logging.getLogger(__name__)

module_dict_key = "github_actions"

URL_PATTERN = r"github.com[/:](?P<org_name>[^/]+)/(?P<repo_name>[^/]+).git"


def get_githubworkflow_api_response(repo_name):
    return requests.get(url=f'https://api.github.com/repos/edx/{repo_name}/actions/workflows')


class GitHubIntegrationHandler:
    """
    sets up the operations and required  github actions workflow CI integration information on instance
    """

    def __init__(self, repo_name):
        self.repo_name = repo_name
        self.api_data = None
        self.github_actions = False
        self._set_github_actions_integration_data()

    def _set_github_actions_integration_data(self):
        self.api_response = get_githubworkflow_api_response(self.repo_name)

    def handle(self):
        """
        initiates the process to fetch github actions workflow integration information
        """
        if self.api_response.status_code == 404:
            logger.error(
                f"An error occurred while fetching github information {self.api_response.content}."
            )
            return

        self.api_data = json.loads(self.api_response.content)

        self.github_actions = [
            True for workflow in self.api_data['workflows']
            if workflow['path'] == '.github/workflows/ci.yml' and workflow['state'] == 'active'
        ]


@add_key_to_metadata(module_dict_key)
def check_githuba_ctions_integration(all_results, git_origin_url):
    """
    Checks repository integrated with github actions workflow
    """
    match = re.search(URL_PATTERN, git_origin_url)
    repo_name = match.group("repo_name")
    integration_handler = GitHubIntegrationHandler(repo_name)
    integration_handler.handle()
    all_results[module_dict_key] = bool(integration_handler.github_actions)
