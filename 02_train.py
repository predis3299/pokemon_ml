"""2단계: 외형으로 종족값 총합(BST)을 예측하고 평균 오차를 비교합니다."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

folder = Path(__file__).resolve().parent
data = pd.read_csv(folder / "data" / "pokemon.csv")
print(f"포켓몬 수: {len(data)}종")
print(data.head())

# 결측값과 중복 행이 있으면 먼저 데이터를 확인합니다.
missing = data.isna().sum().sum()
duplicates = data.duplicated().sum()
print(f"결측값: {missing}개 / 중복 행: {duplicates}개")
if missing or duplicates:
    raise ValueError("결측값 또는 중복 행이 있습니다. data/pokemon.csv를 확인하세요.")

# 1. 80%로 공부하고, 남겨 둔 20%로 실력을 확인합니다.
# random_state를 고정하면 다시 실행해도 같은 포켓몬으로 나뉩니다.
train, test = train_test_split(data, test_size=0.2, random_state=42)
y_train = train["bst"]  # 맞혀야 하는 정답
y_test = test["bst"]
results = []

# 2. 기준선: 외형을 보지 않고 학습 데이터의 평균 BST만 예측합니다.
baseline = DummyRegressor(strategy="mean")
baseline.fit(train[["height_cm"]], y_train)
prediction = baseline.predict(test[["height_cm"]])
results.append({
    "model": "Mean baseline",
    "mae": mean_absolute_error(y_test, prediction),
})

# 3. 같은 모델에 넣는 외형 정보를 바꾸어 두 번 비교합니다.
feature_sets = {
    "Height + weight": ["height_cm", "weight_kg"],
    "All appearance": ["height_cm", "weight_kg", "color", "shape"],
}
for name, columns in feature_sets.items():
    # 색상처럼 글자로 된 값을 0과 1로 바꿉니다.
    x_train = pd.get_dummies(train[columns])
    x_test = pd.get_dummies(test[columns])
    # 학습 때 없던 범주가 있어도 두 표의 열을 같게 맞춥니다.
    x_test = x_test.reindex(columns=x_train.columns, fill_value=0)

    # 여러 결정나무의 예측을 평균 내는 모델입니다.
    model = RandomForestRegressor(
        n_estimators=100, max_depth=5, random_state=42
    )
    model.fit(x_train, y_train)
    prediction = model.predict(x_test)
    results.append({
        "model": name,
        "mae": mean_absolute_error(y_test, prediction),
    })

# 4. MAE는 실제값과 예측값이 평균적으로 몇 점 차이 나는지 나타냅니다.
result = pd.DataFrame(results)
print("\n평균 오차(MAE): 낮을수록 좋습니다.")
print(result.round(2).to_string(index=False))
result.to_csv(folder / "results.csv", index=False)

# 5. 결과를 막대그래프로 저장합니다.
plt.bar(result["model"], result["mae"], color=["gray", "steelblue", "coral"])
plt.ylabel("MAE (BST points)")
plt.title("Predicting Pokemon BST from appearance")
plt.tight_layout()
plt.savefig(folder / "result.png", dpi=150)
plt.close()
print("\nresults.csv와 result.png에 결과를 저장했습니다.")