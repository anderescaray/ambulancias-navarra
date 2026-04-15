# Ambulance Location Optimization in Navarre

## 📌 Project Overview
This project provides a decision-support system for the Department of Health of the Government of Navarre to optimize ambulance deployment. The goal is to ensure rapid emergency response times while balancing service quality with the operational costs of opening headquarters and maintaining units.

---

## 🎯 Mathematical Modeling

### Objective Function
The model minimizes total system costs, including headquarters opening, total ambulances, and population-weighted distance:

$$Minimize \quad Z = 1.5 \cdot N_{sedes} + N_{ambulancias} + 10^{-5} \left( \sum_{j} P_{j} d_{jA} \right)$$

Where:
* $N_{sedes}$: Number of municipalities where a base is established.
* $N_{ambulancias}$: Total number of active ambulances in the network.
* $P_{j}$: Population of municipality $j$.
* $d_{jA}$: Distance from municipality $j$ to its nearest headquarters.

### Quality of Service (SLAs)
The solution strictly adheres to three key constraints:
* **R1 (Broad Coverage):** At least 98% of the population must be within 40 km of an ambulance.
* **R2 (Local Coverage):** At least 80% of the population must be within 20 km of an ambulance.
* **R3 (Availability):** Each station must guarantee an immediate availability probability $\ge 0.8$.

---

## 🧠 Analytical Simplification
A critical design decision was to assign each municipality to its closest headquarters. This was mathematically justified by analyzing the sensitivity of availability probability $P(p)$ relative to population changes $\Delta p$:

$$\Delta P \approx \left| \frac{dP}{dp} \right| \cdot \Delta p \le \epsilon$$

**Proof:** For a station with 1 ambulance and 10,000 inhabitants, the population can increase by up to **3,200 people** without the availability probability dropping more than **1%**. This proves that geographic proximity is the primary driver of service quality, simplifying the problem without compromising the solution.

---

## 🚀 Heuristic Strategy: SA + ALNS
The problem is solved using a hybrid metaheuristic: **Simulated Annealing (SA)** combined with **Adaptive Large Neighborhood Search (ALNS)** mechanisms.

* **Adaptive Neighborhoods:** The algorithm dynamically chooses between adding, removing, or moving a headquarters. Selection probabilities are updated in real-time based on the success of each move.
* **Calibration:** Parameters were tuned through empirical study ($T_0=500$, $T_{min}=0.0000001$, $\alpha=0.95$) to ensure a balance between exploration and convergence.

---

## 📊 Results
The optimal solution identifies **12 strategic headquarters**:
* **Pamplona / Iruña:** Central hub with **2 ambulances**.
* **11 Peripheral Stations:** Located in Altsasu, Andosilla, Cadreita, Cintruénigo, Valle de Egüés, Estella-Lizarra, Liédena, Ribaforada, Doneztebe, Tudela, and Tafalla, each with **1 ambulance**.

The algorithm is highly stable, converging to an objective function value of approximately **76.36** in 90% of test runs.

---

## 📂 Documentation
> **Note:** Detailed academic reports and complete documentation in Spanish are available in the folder `/docs`.

---

## 🌟 Acknowledgments
This project is featured in the **[Awesome Nafarroa](https://github.com/geiserx/awesome-nafarroa)** list, a curated collection of open-source software and projects specific to or developed in Navarre.