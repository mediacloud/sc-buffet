"""
Provide a menu of client-side handlers for orders to the Sous Chef Kitchen API
used by both the CLI and web clients.
"""

import os
import urllib.parse
from http import HTTPStatus
from typing import Any, Dict
from uuid import UUID

import requests
from requests import ConnectionError

from sous_chef_buffet.shared.models import \
    SousChefKitchenAuthStatus, SousChefKitchenSystemStatus

DEFAULT_API_BASE_URL = "https://souschef.ddns.net/api/"
DEFAULT_API_USER_AGENT = "Sous Chef Buffet"

API_AUTH_EMAIL = os.getenv("SC_API_AUTH_EMAIL")
API_AUTH_KEY = os.getenv("SC_API_AUTH_KEY")
API_BASE_URL = os.getenv("SC_API_BASE_URL", DEFAULT_API_BASE_URL)
API_USER_AGENT = os.getenv("SC_API_USER_AGENT", DEFAULT_API_USER_AGENT)


class SousChefKitchenAPIClient:
    """A client for handling interactions with the Sous Chef Kitchen API."""

    def __init__(self, auth_email=API_AUTH_EMAIL, auth_key=API_AUTH_KEY,
        base_url=API_BASE_URL, user_agent=API_USER_AGENT) -> None:
        """Initialize the Sous Chef Kitchen API client."""

        self.auth_email = auth_email
        self.auth_key = auth_key
        self.base_url = base_url
        self.user_agent = user_agent
        
        self._session = self._init_session()


    def _init_session(self) -> requests.Session:
        """Initialize a session with the API."""

        session = requests.Session()
        session.headers.update({'Accept': 'application/json'})
        session.headers.update({"User-Agent": self.user_agent})
        if self.auth_email:
            session.headers.update({'mediacloud-email': self.auth_email})
        if self.auth_key:
            session.headers.update({'Authorization': f'Bearer {self.auth_key}'})
        
        return session
    

    def fetch_all_runs(self) -> Dict[str, Any] | SousChefKitchenAuthStatus:
        """Fetch all Sous Chef Buffet runs from Prefect."""

        expected_responses = {HTTPStatus.OK, HTTPStatus.FORBIDDEN}
        url = urllib.parse.urljoin(self.base_url, "runs/all")

        response = self._session.get(url)
        if response.status_code in expected_responses:
            return response.json()
        response.raise_for_status()


    def fetch_active_runs(self) -> Dict[str, Any] | SousChefKitchenAuthStatus:
        """Fetch any active or upcoming Sous Chef Buffet runs from Prefect."""

        expected_responses = {HTTPStatus.OK, HTTPStatus.FORBIDDEN}
        url = urllib.parse.urljoin(self.base_url, "runs/active")

        response = self._session.get(url)
        if response.status_code in expected_responses:
            return response.json()
        response.raise_for_status()


    def fetch_run_by_id(self, run_id: UUID | str) \
        -> Dict[str, Any] | SousChefKitchenAuthStatus:
        """Fetch a specific Sous Chef Buffet run from Prefect by its ID."""

        expected_responses = {HTTPStatus.OK, HTTPStatus.FORBIDDEN}
        url = urllib.parse.urljoin(self.base_url, f"run/{run_id}")

        response = self._session.get(url)
        if response.status_code in expected_responses:
            return response.json()
        response.raise_for_status()


    def fetch_system_status(self) -> SousChefKitchenSystemStatus:
        """Check whether the Sous Che backend systems are available and ready."""

        expected_responses = {HTTPStatus.OK, HTTPStatus.SERVICE_UNAVAILABLE}
        url = urllib.parse.urljoin(self.base_url, "system/status")

        try:
            response = self._session.get(url)
            if response.status_code in expected_responses:
                return SousChefKitchenSystemStatus.model_validate(response.json())
            response.raise_for_status()
        except ConnectionError as e:
            return SousChefKitchenSystemStatus()
    

    def start_recipe(self, recipe_name:str) -> Dict[str, Any]:
        """Start a Sous Chef recipe."""

        expected_responses = {HTTPStatus.OK, HTTPStatus.FORBIDDEN}
        url = urllib.parse.urljoin(self.base_url, f"recipe/start")
        params = {"recipe_name": recipe_name} # TODO: Allow arbitrary recipe parameters

        response = self._session.post(url, params=params)
        if response.status_code in expected_responses:
            return response.json()
        response.raise_for_status()



    def cancel_recipe(self, recipe_name:str, run_id: UUID | str) -> Dict[str, Any]:
        """Cancel a Sous Chef recipe run."""

        expected_responses = {HTTPStatus.OK, HTTPStatus.FORBIDDEN}
        url = urllib.parse.urljoin(self.base_url, f"runs/cancel")
        params = {"recipe_name": recipe_name, "run_id": run_id}

        response = self._session.post(url, params=params)
        if response.status_code in expected_responses:
            return response.json()
        response.raise_for_status()


    def pause_recipe(self, recipe_name:str, run_id: UUID | str) -> Dict[str, Any]:
        """Pause a Sous Chef recipe run."""

        expected_responses = {HTTPStatus.OK, HTTPStatus.FORBIDDEN}
        url = urllib.parse.urljoin(self.base_url, f"runs/pause")
        params = {"recipe_name": recipe_name, "run_id": run_id}

        response = self._session.post(url, params=params)
        if response.status_code in expected_responses:
            return response.json()
        response.raise_for_status()


    def resume_recipe(self, recipe_name:str, run_id: UUID | str) -> Dict[str, Any]:
        """Resume a Sous Chef recipe run."""

        expected_responses = {HTTPStatus.OK, HTTPStatus.FORBIDDEN}
        url = urllib.parse.urljoin(self.base_url, f"runs/resume")
        params = {"recipe_name": recipe_name, "run_id": run_id}

        response = self._session.post(url, params=params)
        if response.status_code in expected_responses:
            return response.json()
        response.raise_for_status()


    def validate_auth(self) -> SousChefKitchenAuthStatus:
        """Check whether the API key is authorized for Media Cloud and Sous Chef."""

        expected_responses = {HTTPStatus.OK, HTTPStatus.FORBIDDEN}
        url = urllib.parse.urljoin(self.base_url, "auth/validate")

        response = self._session.get(url)
        if response.status_code in expected_responses:
            return SousChefKitchenAuthStatus.model_validate(response.json())
        response.raise_for_status()
