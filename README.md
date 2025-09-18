# Air Quality Forecasting: Additive vs. Machine Learning Models

This repository contains experiments on forecasting **PM₂.₅ and PM₁₀** using a mix of lightweight additive models and machine/deep learning approaches.  

Models implemented:
- **Facebook Prophet (FBP)**
- **NeuralProphet (NP)**
- **LightGBM (LGB)**
- **LSTM (TensorFlow/Keras)**

---

## 📂 Repository Contents
- `main.ipynb` — end-to-end pipeline: preprocessing, training, and evaluation of all models.  
- `weather_data_extraction.ipynb` — data extraction and initial preprocessing from OpenWeather and Open-Meteo APIs.  
- `figures/` — plots and comparative visualizations (train/test forecasts, bar plots, etc.).  
- `README.md` — project documentation.  

---

## 🚀 Usage

1. Run `weather_data_extraction.ipynb` to fetch and preprocess data.
2. Open `main.ipynb` to train models and generate results.
3. Visualizations are saved under `figures/`.

---

## 📈 Key Findings

* **FB Prophet** gave the best generalization with \$R^2 > 0.94\$ on the test horizon.
* **NeuralProphet** leveraged lagged dependencies but had higher errors.
* **LightGBM** fit training data well but failed to generalize.
* **LSTM** captured sequential patterns but needed more data for stability.

👉 **Takeaway:** Lightweight additive models remain strong and interpretable baselines for air-quality forecasting.

---

## 👥 Contributors

* [Moazzam Umer](https://moazzamumer.github.io/) 
* [Hamad Ul Qudous](https://scholar.google.com/citations?user=dZp6IEoAAAAJ&hl=en) 
* [Dr. Asma Ahmad](https://scholar.google.com/citations?user=UYiZXUIAAAAJ&hl=en) 

---

## ✨ Acknowledgments

Data sources: [OpenWeather](https://openweathermap.org/api), [Open-Meteo](https://open-meteo.com/).
Libraries: Prophet, NeuralProphet, LightGBM, TensorFlow/Keras.
