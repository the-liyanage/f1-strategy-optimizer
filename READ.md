# 🏎️  F1 Pit Stop Strategy Optimizer
An end-to-end machine learning system that predicts the optimal lap to pit and recommends tyre strategies using real Formula 1 telemetry data. 
Built with XGBoost, PyTorch LSTM, Fast API, and deployed with Docker.

## 📌 What is this Project?
In Formula 1, pit stop timing is one of the most important strategic decisions a team makes during a race. Pit too early and you lose track postiion. Pit too late and your tyres are completely degraded, costing you seconds every lap.


This project builds an ML system that answers two questions:
1. Should this driver pit this lap? (XGBoost classifier)

2. How will this tyre degrade over the next 10 laps (PyTorch LSTM)

It then combines both answers into a strategy engine that recommends the optimal pit window and tyre compound - and serves those recommendations through a live web app.


## Why This Problem?
- Real F1 teams (Mercedes, Ferrari, Red Bull) spen millions solving this exact problem.
- It combines classical ML + deep learning in one project
- The data is real, free and publicly available via FastF1
- It has a clear, explainable output: *Pit Hamilton on lap 28, switch to Medium*
- It can be deployed as a live app with a public URL



## 🏗️ Architecture Overview

 ```
 ┌─────────────────────────────────────┐
                    │           FastF1 API                │
                    │  (real F1 lap + telemetry data)     │
                    └──────────────┬──────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │         Data Pipeline               │
                    │  fetch_data.py → feature_eng.py     │
                    │  Cleans, transforms, engineers      │
                    │  features from raw lap data         │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
        ┌───────────────────┐       ┌─────────────────────────┐
        │  XGBoost Model    │       │   PyTorch LSTM Model    │
        │                   │       │                         │
        │  "Should we pit   │       │  "How will lap times    │
        │   this lap?"      │       │   evolve over the       │
        │  (classification) │       │   next 10 laps?"        │
        │                   │       │  (time series forecast) │
        └─────────┬─────────┘       └────────────┬────────────┘
                  │                              │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │       Strategy Engine        │
                  │  Combines both model outputs │
                  │  + undercut/overcut logic    │
                  │                              │
                  │  Output:                     │
                  │  "Pit on lap 28 → Medium"    │
                  │  "Projected gain: +2.3s"     │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │        FastAPI Backend       │
                  │  Serves predictions via API  │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │      Streamlit Frontend      │
                  │  Pick a race, pick a driver  │
                  │  Get strategy recommendations│
                  └──────────────────────────────┘


```


