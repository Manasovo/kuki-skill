mport spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from requests import HTTPError
import time

from mycroft.api import DeviceApi
from mycroft.util.log import LOG

def get_token(dev_cred):
    """ Get token with a single retry.
    Args:
        dev_cred: OAuth Credentials to fetch
     """
    retry = False
    try:
        d = DeviceApi().get_oauth_token(dev_cred)
    except HTTPError as e:
        if e.response.status_code == 404:  # Token doesn't exist
            raise
        if e.response.status_code == 401:  # Device isn't paired
            raise
        else:
            retry = True
    if retry:
        d = DeviceApi().get_oauth_token(dev_cred)
    return d


class MycroftKukiCredentials(SpotifyClientCredentials):
    """ Credentials object renewing through the Mycroft backend."""
    def __init__(self, dev_cred):
        self.dev_cred = dev_cred
        self.access_token = None
        self.expiration_time = None
        self.get_access_token()

    def get_access_token(self, force=False):
        if (not self.access_token or time.time() > self.expiration_time or
                force):
            d = get_token(self.dev_cred)
            self.access_token = d['access_token']
            # get expiration time from message, if missing assume 1 hour
            self.expiration_time = d.get('expiration') or time.time() + 3600
        return self.access_token


def refresh_auth(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except HTTPError as e:
            if e.response.status_code == 401:
                self.client_credentials_manager.get_access_token(force=True)
                return func(self, *args, **kwargs)
            else:
                raise
    return wrapper


class KukiConnect(spotipy.Spotify):
    """ Implement the Spotify Connect API.
    See:  https://developer.spotify.com/web-api/

    This class extends the spotipy.Spotify class with Spotify Connect
    methods since the Spotipy module including these isn't released yet.
    """