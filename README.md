# Kompaktowa wyszukiwarka

Kompaktowy serwis do wyszukiwania krótkich tekstów podobnych do przesłanego promptu.  
System wykorzystuje embeddingi generowane przez model (SentenceTransformer) i przechowuje je w bazie wektorowej **Qdrant**.  
Przesyłane prompty zapisywane są w historii w bazie danych **Redis**.  

---

## Architektura

- **FastAPI** - Główny framework do budowy API i obsługi serwera HTTP (uvicorn). Oprócz tego zarządza serwisami Qdrant i Redis.
- **Qdrant** - Baza wektorowa do przechowywania wygenerowanych embeddingów i wyszukiwania podobnych treści.
- **Redis** - Baza danych do przechowywania historii promptów.

---

## Wymagania wstępne
- **Docker** (>= 23.0)

---

## Instrukcje uruchomienia

```bash
git clone https://github.com/Infinity080/wyszukiwarka && cd wyszukiwarka/
docker compose up --build
```

UWAGA:  
przed pierwszym wyszukiwaniem musisz załadować zbiór danych i wygenerować embeddingi za pomocą:
```bash
curl -X POST http://localhost:8000/ingest
```

## Testy

Serwis przychodzi razem z zestawem testów do sprawdzenia funkcjonalności endpointów API.  
Możemy je odpalić za pomocą komendy:
```bash
docker compose run --rm app pytest --asyncio-mode=auto
```

---

## Decyzje projektowe

- **Qdrant** > **Milvus**, ponieważ:
    - jest prostszy. Do przechowywania i wywoływania małej liczby embeddingów będzie działał szybciej,
    - lepiej sobie radzi z modelami działającymi na CPU,
    - jest bardzo wygodny w implementacji w pythonie i jestem z nim zaznajomiony.

- **Długość wektora** = 384, ponieważ 
    - użyty model "all-MiniLM-L6-v2" generuje embeddingi o wymiarze 384.

- **Metryka cosinusowa**, ponieważ:
    - metryka euklidesowa nie bierze pod uwagę kierunku wektora, który jest kluczowy w embeddingach tekstowych,
    - (tak było w wymaganiach :D).

- **Embeddingi:** 
    - generowane przez model "all-MiniLM-L6-v2", ponieważ jest lekki, działa na CPU oraz generuje wystarczająco dobre embeddingi do naszych tekstów,
    - enkodowane są konkatenacje kolumn zawierających: krótki opis, wprowadzenie, fragment i dodatkowe notatki.

--- 

## Dodatkowe

- **Trwałość danych**, osobne wolumeny dla Qdrant i Redis w docker-compose.yml,
- **Logowanie** w formacie JSON do pliku i strumienia (timestamp, request_path, status_code, method, duration).

## Format danych                  

Zbiór danych pochodzi z https://www.kaggle.com/datasets/kononenko/commonlit-texts.  
Plik CSV w data/commonlit_texts.csv z kolumnami:  
- id,
- description,
- intro,
- excerpt,
- notes,
- metadata (reszta kolumn).

## Prezentacja działania

Dokładną dokumentację API udostępnioną przez OpenAPI możesz obejrzeć na:
[http://localhost:8000/docs](http://localhost:8000/docs)  
Przykładowe requesty do sprawdzenia endpointów:

### Instalacja curl

Aby móc ręcznie wysyłać requesty HTTP, musimy zainstalować odpowiednie narzędzie np. **curl** lub **Postman**.
```bash
sudo apt update && sudo apt install -y curl
```

### Ładowanie danych

Najpierw musimy załadować zbiór danych i wygenerować endpointy.  
**/ingest** odpowiada za ładowanie datasetu, generowanie embeddingów i przygotowywanie odpowiednich serwisów.

```bash
curl -X POST http://localhost:8000/ingest
```

### Health check

**/healthz** zwraca status serwera, w tym Qdrant i Redis.

```bash
curl -X GET http://localhost:8000/healthz
```

### Logika wyszukiwania

**/search** odpowiada za właściwą logikę wyszukiwarki.  
W pliku data/sample.jsonl jest przygotowane przykładowe 20 promptów do szybkiego sprawdzenia działania.  
Wybieramy jakiś prompt, podstawiamy **q** i **k** i wysyłamy poprzez:
```bash
curl -X POST http://localhost:8000/search?q=test%20query&k=5
```

### Podglądanie dokumentów

Każdy dokument w naszym zbiorze możemy podejrzeć po jego id, posłuży nam do tego **/doc/{id}**    
Na przykład, aby podejrzeć pierwszy dokument wysyłamy:

```bash
curl -X GET http://localhost:8000/doc/0
```

### Statystyki

Aby sprawdzić statystyki naszego zbioru danych, requestujemy:
```bash
curl -X GET http://localhost:8000/stats
```

### Ostatnie zapytania

Możemy podejrzeć ostatnie wysłane zapytania poprzez endpoint **/queries/recent** z opcjonalnym parametrem **limit**:
```bash
curl -X GET http://localhost:8000/queries/recent?limit=3
```

