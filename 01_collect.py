"""1단계: PokéAPI에서 포켓몬의 외형과 종족값을 가져옵니다."""
from pathlib import Path
import time

import pandas as pd
import requests

folder = Path(__file__).resolve().parent
csv_path = folder / "data" / "pokemon.csv"

# 한 번 수집한 데이터가 있으면 API를 다시 호출하지 않습니다.
if csv_path.exists():
    print(f"저장된 데이터 {len(pd.read_csv(csv_path))}종을 사용합니다.")
    print("다시 수집하려면 data/pokemon.csv를 다른 이름으로 보관한 뒤 실행하세요.")
    raise SystemExit()

session = requests.Session()


def get_json(url):
    response = session.get(url, timeout=30)
    response.raise_for_status()  # 통신이 실패하면 멈추고 오류를 보여줍니다.
    return response.json()


# 목록이 여러 페이지이므로 다음 페이지가 없을 때까지 가져옵니다.
species_list = []
url = "https://pokeapi.co/api/v2/pokemon-species/?limit=200"
while url:
    page = get_json(url)
    species_list.extend(page["results"])
    url = page["next"]

rows = []
for number, item in enumerate(species_list, start=1):
    species = get_json(item["url"])

    # 같은 종에 여러 형태가 있으면 공식 기본 형태 하나만 선택합니다.
    default = next(v for v in species["varieties"] if v["is_default"])
    pokemon = get_json(default["pokemon"]["url"])

    rows.append({
        "name": species["name"],
        "height_cm": pokemon["height"] * 10,
        "weight_kg": pokemon["weight"] / 10,
        "color": (species.get("color") or {}).get("name", "unknown"),
        "shape": (species.get("shape") or {}).get("name", "unknown"),
        "bst": sum(stat["base_stat"] for stat in pokemon["stats"]),
    })
    if number % 100 == 0:
        print(f"{number}/{len(species_list)}종 수집 완료")
    time.sleep(0.15)  # 서버에 연속해서 너무 빠르게 요청하지 않기 위한 대기

csv_path.parent.mkdir(exist_ok=True)
pd.DataFrame(rows).to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"{len(rows)}종 저장 완료: {csv_path}")