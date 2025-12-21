# 📈 Crypto Aggregator & Analytics

Асинхронный микросервис на **FastAPI** для агрегации цен криптовалют с внешних бирж, их анализа и визуализации. 
Проект реализует принципы **Clean Architecture** и паттерны проектирования.

## 🚀 Возможности

*   **Мульти-сорсинг:** Параллельный сбор цен с **Binance** и **CoinGecko**.
*   **Аналитика:** Расчет min/max/avg, спреда и поиск аномалий (выбросов).
*   **Визуализация:** Генерация графиков цен (PNG) с фильтрацией по периодам (`24h`, `7d`, `30d`, `1y`).
*   **Кэширование:** In-Memory Cache для снижения нагрузки на внешние API.

## 🛠 Стек технологий
*   **Язык:** Python 3.10+
*   **Web:** FastAPI, Uvicorn
*   **Аналитика:** Pandas
*   **Графики:** Matplotlib
*   **Контейнеризация:** Docker

## 🏗 Архитектура

```mermaid
flowchart TB
    User(("👤 Client")) -- Requests --> Router["API"]
    Router -- "1. Get Data" --> Aggregator["Price Aggregator"]
    Aggregator -- Returns Data --> Router
    Router -- "2. Calculate" --> Analytics["Analytics Service"]
    Router -- "3. Draw" --> Visualizer["Graph Service"]
    Aggregator -- Check --> Cache["⚡ In-Memory Cache"]
    Aggregator -- Fetch --> BinClient["Binance Client"] & GeoClient["CoinGecko Client"]
    BinClient <-- HTTP/JSON --> BinAPI["🟡 Binance API"]
    GeoClient <-- HTTP/JSON --> GeoAPI["🟢 CoinGecko API"]

     BinAPI:::external
     GeoAPI:::external
     User:::client
     Router:::api
     Aggregator:::logic
     Analytics:::logic
     Visualizer:::logic
     Cache:::infra
     BinClient:::infra
     GeoClient:::infra
    classDef client fill:#f9f,stroke:#333,stroke-width:2px
    classDef api fill:#ade,stroke:#333,stroke-width:2px
    classDef logic fill:#f96,stroke:#333,stroke-width:2px
    classDef infra fill:#ff9,stroke:#333,stroke-width:2px
    classDef external fill:#ddd,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
```


## 🚀 Как запустить проект(должен быть установлен Git и Docker):

1.  **Скачайте проект:**
    Откройте терминал и введите:
    ```
    git clone https://github.com/Keyloner/crypto-aggregator.git
    cd crypto-aggregator
    ```

2.  **Соберите приложение:**
    ```
    docker build -t crypto-app .
    ```

3.  **Запустите:**
    ```
    docker run -p 8000:8000 crypto-app
    ```

4.  **Готово!** Откройте в браузере: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)