# 👕 AR Virtual Try-On System

### Walmart Sparkathon 2025 Submission

---

## 🚀 Project Overview

This project is an **Augmented Reality Virtual Try-On System** developed as part of Walmart Sparkathon 2025. It allows users to virtually try on different shirts with various sizes and color overlays in real-time using their webcam feed.

---

## ✨ Features

* 🔴 **Real-time AR try-on** with pose detection using YOLOv8 pose estimation
* 👕 **Multiple shirt options** to switch instantly
* 🎨 **Dynamic color overlay** (red, green, blue, yellow, magenta, cyan, white)
* 📏 **Size adjustments** (small, medium, large scaling)
* ➡️ **Position adjustments** to align shirts precisely on user body
* 💻 **Interactive web interface** built with Flask and OpenCV

---

## 💡 Problem Statement

**In-store fitting rooms face hygiene, privacy, and operational challenges.**
This AR Try-On system addresses:

* Long queues at trial rooms
* Limited availability of sample sizes or colors
* Consumer hesitation in physically trying apparel

It enhances the **customer shopping experience by enabling quick virtual fitting** without physical contact, aligning with Walmart’s vision for seamless and immersive retail experiences.

---

## 🛠️ Tech Stack

* **Python**
* **Flask** – Web framework
* **OpenCV** – Real-time video processing and overlay
* **Ultralytics YOLOv8 Pose** – Human keypoint detection for shirt alignment
* **HTML & CSS** – Frontend styling

---

## 🔧 Installation & Usage

1. **Clone the repository:**

   ```bash
   git clone <repository-link>
   cd <project-folder>
   ```

2. **Install dependencies:**

   ```bash
   pip install flask opencv-python ultralytics
   ```

3. **Download YOLOv8 pose model weights** (if not already downloaded):

   * Place `yolov8n-pose.pt` in the project root.

4. **Organize resources:**

   * Create a `Resources/Shirts` folder.
   * Add your shirt PNG images named `shirt1.png`, `shirt2.png`, etc.

5. **Run the application:**

   ```bash
   python try_on_video.py
   ```

6. **Access the web interface:**

   * Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🎥 Demo

>[Click here to look demo] (*https://youtu.be/WUU12pEqZyE*)

---

## 📝 Project Structure

```
try_on_video.py
Resources/
 └── Shirts/
      ├── shirt1.png
      └── shirt2.png
yolov8n-pose.pt
```

---

## 🧠 Future Enhancements

* Integration with e-commerce product catalogues for direct purchase
* AR try-on for other apparel categories (trousers, jackets)
* Multi-user support with cloud-based processing
* WebAR integration for mobile browser support

---

## 👤 Author

* **Yeshta Shri**
* Walmart Sparkathon 2025 Team

---

## 📄 License

This project is for educational and hackathon demonstration purposes under Walmart Sparkathon 2025 guidelines.




