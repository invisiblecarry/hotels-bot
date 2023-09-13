from config_data import config
from requests import get, codes, post


def api_request(method_endswith,  # Varies depending on request. locations/v3/search or properties/v2/list
                params,  # Parameters, if locations/v3/search, then {'q': 'Riga', 'locale': 'ru_RU'}
                method_type  # Method\Type of request GET\POST
                ):
    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"

    # # Depending on the type of request, call the appropriate function
    if method_type == 'GET':
        return get_request(
            url=url,
            params=params
        )
    if method_type == 'POST':
        return post_request(
            url=url,
            params=params
        )
    else:
        return None


def get_request(url, params):  # get request function
    try:
        response = get(
            url,
            headers={
                "X-RapidAPI-Key": config.RAPID_API_KEY,
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            },
            params=params,
            timeout=15
        )
        if response.status_code == codes.ok:
            return response

    except Exception as ex:
        raise ex


def post_request(url, params):  # post request function
    try:
        response = post(
            url,
            headers={
                "content-type": "application/json",
                "X-RapidAPI-Key": config.RAPID_API_KEY,
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"

            },
            json=params,
            timeout=15
        )
        if response.status_code == codes.ok:
            return response

    except Exception as ex:
        raise ex
