# 🧭 RouteWise - Multi-Stop Trip Optimizer with Google Maps export

**RouteWise** is a powerful, user-friendly tool that helps anyone plan the **shortest round-trip through multiple locations**, based on **real road travel time** — something Google Maps doesn’t do natively.

Whether you're running errands or planning deliveries, RouteWise ensures you're taking the **most efficient route**, with turn-by-turn navigation ready to open in Google Maps.

---

## 🚗 Why RouteWise?

Most mapping apps let you add multiple stops — but **don’t optimize the order**. You're left guessing how to rearrange them for the fastest loop. RouteWise fixes that.

> 📍 Input up to 15 locations  
> ⚡ Get the optimized route (fastest total travel time)  
> 🗺️ View it on an interactive map  
> 📲 Export directly to Google Maps for navigation

---

## 🛠️ Features

- 🔎 **Flexible address input** – Paste any real-world address, landmark, or place name
- 📍 **Accurate geolocation** – Uses Nominatim (OpenStreetMap) for free address-to-coordinate conversion
- 🛣️ **True travel-time optimization** – Fetches actual road durations using OSRM (Open Source Routing Machine)
- 🧠 **TSP-powered route solver** – Finds the shortest loop visiting all stops once and returning home
- 🗺️ **Visual mapping** – Interactive Leaflet map with numbered markers and colored path
- 📤 **One-click Google Maps export** – Open your optimized route in your default Maps app instantly
- 💻 **Runs locally in browser** – No login, no account, no ads, no tracking

---

## 🧠 How It Works

1. **Geocoding**  
   Each input address is translated into precise coordinates using **Nominatim**, a free and open geocoding API powered by OpenStreetMap.

2. **Travel Matrix**  
   For every pair of locations, RouteWise queries **OSRM's `/table` API** to get the actual travel durations (not straight-line distances).

3. **Route Optimization**  
   It solves a classic **Traveling Salesman Problem (TSP)** using the **Held–Karp algorithm** (dynamic programming) to find the path with the lowest total travel time.

4. **Map Rendering**  
   The optimized path is visualized using **Folium**, built on **Leaflet.js**, with numbered markers and colored polylines.

5. **Navigation Launch**  
   Finally, a Google Maps URL is auto-generated with the optimized stop order, ready to open on any device for real navigation.

---

## 💡 Example Use Case

> **Riya**, a university student, needs to visit 10 stores across the city and return home.  
> She enters the addresses, clicks "Optimize Route," and within seconds sees the shortest timed loop.  
> She avoids backtracking, saves over 35% in fuel and time, and opens the optimized route directly in Google Maps.

---

## 🧰 Tech Stack

| Layer           | Technology                         |
|------------------|--------------------------------------|
| Frontend         | **Streamlit**, **Folium (Leaflet.js)** |
| Backend          | **Python**                           |
| Geocoding        | **Nominatim API (OpenStreetMap)**    |
| Routing Engine   | **OSRM `/table` API** (Travel Time)  |
| Optimization     | **Held–Karp TSP Solver**             |

---

## 🚀 Why It Stands Out

- ✅ Fully free & open source
- ✅ No account, no paywall, no analytics
- ✅ Works offline (after initial geocoding)
- ✅ Solves a real user pain point Google Maps doesn't address
- ✅ Useful for students, travelers, couriers, and casual users

---

## 🌱 Future Upgrades

- 🔁 Non-looping routes (e.g., start at A, end at Z)
- 🚦 Traffic-aware optimization via Google Directions or Mapbox
- 📥 Upload from CSV or Google Sheets

---

## 👨‍💻 Author

Built with purpose by **Mudit Mayank Jha**  
🎓 B.Sc. Computer Science @ University of the West Indies  
🇺🇸 <img src="https://upload.wikimedia.org/wikipedia/en/a/a4/Flag_of_the_United_States.svg" alt="US Flag" width="20" style="vertical-align: middle;"/> Academic Exchange at University of Richmond  
🔗 [GitHub](https://github.com/muditjha20)

---

> ⭐ Found this useful? Star the repo or share with someone who still drags addresses around in Google Maps.
