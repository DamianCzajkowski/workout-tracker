import asyncio
import os
from httpx import AsyncClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

APP_ID = os.getenv("APP_ID")
API_KEY = os.getenv("API_KEY")
SHEETY_TOKEN = os.getenv("SHEETY_TOKEN")
HEADERS = {"x-app-id": APP_ID, "x-app-key": API_KEY}
TRACK_HOST = "https://trackapi.nutritionix.com"
EXERCISE_ENDPOINT = "/v2/natural/exercise"
SHEETY_HOST = "https://api.sheety.co/f1003f9ab7abd9d0f48bcdc38a238779"
WORKOUT_ENDPOINT = "/workoutTracking/workouts"
GENDER = "male"
WEIGHT_KG = "86"
HEIGHT_CM = "184"
AGE = "23"


async def get_exercise_stats(input: str):
    payload = {
        "query": input,
        "gender": GENDER,
        "weight_kg": WEIGHT_KG,
        "height_cm": HEIGHT_CM,
        "age": AGE,
    }
    async with AsyncClient(base_url=TRACK_HOST, headers=HEADERS) as client:
        try:
            resp = await client.post(url=EXERCISE_ENDPOINT, json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as err:
            print(f"ERROR: {err}")


async def save_exercises_in_google_sheet(input: dict):
    datetime_now = datetime.now()
    payload = {
        "workout": {
            "date": datetime_now.strftime("%d/%m/%Y"),
            "time": datetime_now.strftime("%H:%M:%S"),
            "exercise": input["name"],
            "duration": input["duration_min"],
            "calories": input["nf_calories"],
        }
    }
    async with AsyncClient(
        base_url=SHEETY_HOST, headers={"authorization": f"Bearer {SHEETY_TOKEN}"}
    ) as client:
        try:
            resp = await client.post(url=WORKOUT_ENDPOINT, json=payload)
            resp.raise_for_status()
        except Exception as err:
            print(f"ERROR: {err}")


async def get_rows():
    async with AsyncClient(
        base_url=SHEETY_HOST, headers={"authorization": f"Bearer {SHEETY_TOKEN}"}
    ) as client:
        response = await client.get(
            url=WORKOUT_ENDPOINT,
        )
        print(response.json())


async def main():
    user_input = input("Tell me which exercises you did: ")
    exercises_stats = await get_exercise_stats(user_input)
    for exercise in exercises_stats["exercises"]:
        await save_exercises_in_google_sheet(input=exercise)


if __name__ == "__main__":
    asyncio.run(main())
