import requests
from dotenv import load_dotenv

load_dotenv()

def main():

    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            'client_id': '169192',
            'client_secret': '6187a6fb2128f825625fe81a35c16fe6cc9570e2',
            'code': 'ac7acdf27fa5bb03b80bd568bd8b61305f305dff',
            'grant_type': 'authorization_code'
        },
        verify=False
    )

    tokens = response.json()
    print(tokens)

    # response = requests.get("https://www.strava.com/api/v3/segments/6821922/leaderboard",
    #                         headers={"Authorization": "Bearer 73725f7af2f6468c0bea57e8464ea273a100b74c"},
    #                         verify=False)
    # print(response.json())

if __name__ == "__main__":
    main()
