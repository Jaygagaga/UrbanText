import requests
from functools import partial
class LTSession(requests.Session):
    def __init__(self, workspace:str,user:str,pwd:str,host:str=None):
        """[summary]
        Initializes a LightTag API session object
        Arguments:
            workspace {str} -- [The name of your workspace]
            user {str} -- [Your LightTag Username]
            pwd {str} -- [Your LightTag password]

        Keyword Arguments:
            host {str} -- [Optional, use this when self hosting LightTag ] (default: {None})
        """
        super().__init__()
        if host is None:
            host = 'https://{workspace}.lighttag.io/api/'.format(workspace=workspace)
        token =self._authenticate(host,user,pwd)
        self.headers.update({"Authorization":"Token {token}".format(token=token)})
        def new_request(f, method, url, *args, **kwargs):
            if '://' not in url:  
                return f(method,host + url, *args, **kwargs)  
            else:
                return f(method,url,*args,**kwargs)
        self.request = partial(new_request, self.request)
        def check_for_errors(resp,*args,**kwargs):
            resp.raise_for_status()
        self.hooks['response'] = [check_for_errors]

    @staticmethod
    def _authenticate(host:str,user:str,pwd:str):
        """Fetches authentication token based on username password

        Arguments:
            host {str} -- [Fully qualified host name]
            user {str} -- [LightTag Username]
            pwd {str} -- [LightTag Password]
        """
        response = requests.post(host+'auth/token/login/',json={"username":user,"password":pwd})
        response.raise_for_status()
        data = response.json()
        token = data['key']
        is_manager = data['is_manager']
        if not is_manager:
            raise Exception("Your are not a manager")
        return token

