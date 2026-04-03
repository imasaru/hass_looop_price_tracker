# hass_looop_price_tracker

[Looop でんき](https://looop-denki.com/)の電力料金情報をHome Assistantで監視できる統合です。

## 概要

この統合により、Looop でんきの「でんき予報」データをリアルタイムで取得し、Home Assistantのセンサーとして表示できます。電力料金の変動を監視して、電気代の節約や自動化に活用できます。

## 機能

- **リアルタイム電力料金監視**: 30分単位で更新される現在の電力料金
- **価格ステータス表示**: でんき日和、でんき注意報、でんき警報の判定
- **バイナリセンサー**: 安い時間帯・高い時間帯をオン/オフで直接表現するセンサー（自動化条件に最適）
- **暖房オーバーシュート遮断ブループリント**: 部屋が設定温度を大幅に超えた場合に暖房を自動停止し、ヒステリシス付きで再起動する自動化ブループリント（EN 16798-1 / EN ISO 52120-1 準拠）
- **価格連動暖房制御ブループリント**: 電気代が高い時間帯に暖房を一時停止・エコモードへ切り替える汎用ブループリント

<!--
## インストール

### HACS経由（推奨）
1. HACSを開く
2. 「統合」→「カスタムリポジトリ」
3. リポジトリURL を追加
4. 「Looop でんき」を検索してインストール
5. Home Assistantを再起動

### 手動インストール
1. `custom_components/looop_denki/` フォルダを作成
2. 統合ファイルをフォルダにコピー
3. Home Assistantを再起動
-->

## 設定

1. **統合の追加**
   - 設定 → デバイスとサービス → 統合を追加
   - 「Looop でんき」を検索
   - または直接URL: `/config/integrations/add?domain=looop_denki`

2. **電力エリア選択**
   - お住まいの電力エリアを選択してください
   - 東京電力エリアの場合は「03 - 東京電力」を選択

3. **完了**
   - 統合が正常に設定されると、センサーが作成されます

## センサー情報

### メインセンサー: `sensor.looop_denki_current_price_*`

- **値**: 現在の電力料金（円/kWh）
- **単位**: 円/kWh
- **更新間隔**: 5分

### バイナリセンサー

| エンティティ | 説明 |
|---|---|
| `binary_sensor.<area>_cheap_now` | `ON` = でんき日和（電気代が安い時間帯） |
| `binary_sensor.<area>_price_alert` | `ON` = でんき注意報またはでんき警報（電気代が高い時間帯） |

これらのバイナリセンサーは自動化の条件やブループリントの inhibit 入力として直接使用できます。

### 属性

| 属性名 | 説明 | 例 |
|--------|------|-----|
| `current_level` | 価格レベル（-0.5〜0.5） | -0.5 |
| `current_text` | 詳細情報 | "Price: 12.3, Level: -0.5" |
| `status` | 価格ステータス | "でんき日和" |
| `time_slot` | 30分単位のタイムスロット | 24 |
| `hour` | 現在の時間 | 12 |
| `minute_range` | 分の範囲 | "00-29" |

### 価格ステータス

- **でんき日和** 🌞: 電力料金が安い時間帯（電気使用推奨）
- **でんき注意報** ⚠️: 電力料金が高い時間帯（使用を控えめに）
- **でんき警報** 🚨: 電力料金が非常に高い時間帯（100円/kWh以上）

## 自動化の例

### 安い時間帯に洗濯機を動かす

```yaml
automation:
  - alias: "安い電気で洗濯"
    trigger:
      - platform: state
        entity_id: binary_sensor.looop_denki_03_cheap_now
        to: "on"
    condition:
      - condition: time
        after: "22:00:00"
        before: "06:00:00"
    action:
      - service: switch.turn_on
        entity_id: switch.washing_machine
```

### 高い時間帯に通知

```yaml
automation:
  - alias: "電気代高騰通知"
    trigger:
      - platform: state
        entity_id: binary_sensor.looop_denki_03_price_alert
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "⚠️ 電力料金が高騰しています！電気の使用を控えましょう"
```

## 暖房オーバーシュート遮断 & 価格連動制御ブループリント

このリポジトリには、Looop でんきの価格センサーと組み合わせて使える Home Assistant 自動化ブループリントが含まれています。

### ファイル場所

```
blueprints/automation/looop_denki/hvac_overshoot_price_policy.yaml
```

### インポート方法

1. HA の「設定」→「自動化」→「ブループリント」→「ブループリントをインポート」
2. 上記 YAML ファイルのパスまたは GitHub URL を指定

### 機能概要

#### 1. 暖房オーバーシュート遮断（ヒステリシス付きラッチ）

EN 16798-1 Category II 快適温度帯（±1.0°C）に基づき、部屋が設定温度を大幅に上回った場合に暖房を自動停止します。設定温度近辺まで温度が下がり、かつ最小停止時間が経過するまで暖房は再起動しません（ラッチ動作）。

| 設定項目 | 説明 | デフォルト |
|---|---|---|
| オーバーシュート閾値 | 設定温度超過でシャットオフするΔ°C | 1.5°C |
| 解除閾値 | 再起動を許可する設定温度との差Δ°C | 0.5°C |
| 最小停止時間 | シャットオフ後の最低停止時間 | 30 分 |
| 暖房再起動モード | 解除後に設定するHVACモード | heat |

#### 2. 価格連動暖房ポリシー

`binary_sensor.<area>_price_alert` や任意の `input_boolean` / スケジュールエンティティを inhibit 信号として使用し、電気代が高い時間帯の暖房動作を制御します。

| ポリシー | 説明 |
|---|---|
| `pause_heating` | 暖房を停止（HVAC off） |
| `force_eco` | エコ設定温度（任意）に切り替え |
| `block_boost` | 現在の設定温度を維持（昇温禁止） |

### ブループリント設定例

```yaml
# HA 自動化で使用する場合
use_blueprint:
  path: looop_denki/hvac_overshoot_price_policy.yaml
  input:
    climate_entity: climate.living_room_ac
    overshoot_enabled: true
    overshoot_threshold_k: 1.5
    release_threshold_k: 0.5
    minimum_off_minutes: 30
    heating_resume_mode: heat
    price_inhibit_entity: binary_sensor.looop_denki_03_price_alert
    price_policy: pause_heating
    eco_setpoint: 18.0
    enable_logging: true
```

## トラブルシューティング

### センサーが利用不可能

1. **ネットワーク接続確認**
   - Home Assistantからインターネットにアクセスできるか確認

2. **ログ確認**
   ```yaml
   logger:
     default: info
     logs:
       custom_components.looop_denki: debug
   ```

3. **統合の再読み込み**
   - 設定 → デバイスとサービス → Looop でんき → 再読み込み

## ライセンス

MIT License

## 免責事項

- この統合は非公式のサードパーティ製品です
- Looop でんき社とは無関係です
- データの正確性は保証されません
- 重要な判断は公式サイトでご確認ください

---

💡 **ヒント**: Home Assistantのエネルギーダッシュボードと組み合わせて、電力消費と料金の両方を監視しましょう！
