# HYPERSPECTRAL IMAGE CLASSIFICATION — INTERVIEW GUIDE
## IEEE TGRS Research Project Deep Dive

---

## 📌 PROJECT OVERVIEW

**What is Hyperspectral Imaging?**

Hyperspectral images capture data across hundreds of spectral bands (wavelengths), 
not just RGB like normal cameras. Each pixel contains a complete spectral signature 
that can identify materials, vegetation, minerals, etc.

**Example:**
- Normal camera: Pixel = [Red, Green, Blue] = 3 values
- Hyperspectral: Pixel = [400nm, 401nm, 402nm, ... 700nm] = 200+ values

**What This Project Does:**

Classifies each pixel in a hyperspectral image into land-cover classes 
(roads, vegetation, water, buildings, etc.)

---

## 🏗️ ARCHITECTURE & WORKFLOW

### Complete Pipeline:

```
Raw Hyperspectral Image (Indian Pines Dataset)
        │
        ▼
┌─────────────────────────────────────────────┐
│  1. PREPROCESSING                            │
│  • PCA Dimensionality Reduction              │
│  • Reduces 200 bands → 15-20 principal       │
│    components (removes noise)                │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│  2. SPECTRAL-SPATIAL EXTRACTION (3D CNN)     │
│  • 3×3 Local Branch: Captures fine details    │
│  • 5×5 Global Branch: Captures context        │
│  • Parallel processing → Combined features   │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│  3. GAUSSIAN WEIGHTED TOKENIZATION            │
│  • Divides features into patches             │
│  • Assigns importance weights                │
│  • Prepares for Transformer input             │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│  4. TRANSFORMER ENCODER                      │
│  • Multi-head Self-Attention                 │
│  • Captures long-range dependencies          │
│  • 4 attention heads                         │
└─────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│  5. CLASSIFICATION HEAD                       │
│  • Pixel-wise classification                 │
│  • 16 classes (Indian Pines)                 │
│  • Softmax output                            │
└─────────────────────────────────────────────┘
        │
        ▼
Classification Map (Color-coded)
```

---

## 🔑 KEY INNOVATION: Dual-Scale Feature Extraction

### Why Dual-Scale?

**Problem with single-scale:**
- 3×3 conv: Good for fine details, poor context
- 5×5 conv: Good for context, misses fine details

**Solution:** Parallel branches!

```
Input Features
      │
      ├──→ 3×3 Conv Branch ──→ Fine Details (edges, textures)
      │
      └──→ 5×5 Conv Branch ──→ Global Context (structures)

Both outputs are concatenated to get the best of both worlds!
```

**Why this improves accuracy:**
- Local features: Identify individual objects
- Global features: Understand spatial relationships
- Combined: Better classification in complex scenes

---

## 📊 RESULTS & COMPARISON

| Method | Indian Pines | Pavia University | Houston |
|--------|-------------|------------------|---------|
| Standard CNN | 89.1% | 87.5% | 85.2% |
| **Our DS-SSFTT** | **94.2%** | **91.8%** | **88.9%** |
| Improvement | +5.1% | +4.3% | +3.7% |

---

## ⚠️ CHALLENGES & SOLUTIONS

### Challenge 1: Implementing from Research Paper

**Problem:**
- Paper had complex architecture
- Missing implementation details
- Many hyperparameters not specified

**Solution:**
- Read paper 5+ times
- Referred to similar implementations
- Experimented with hyperparameters
- Kept what worked, modified what didn't

---

### Challenge 2: High Dimensionality

**Problem:**
- Indian Pines: 200 spectral bands
- Each band = 145×145 pixels
- Total: 200 × 145 × 145 = 4.2M values per image

**Solution:**
- PCA reduction: 200 → 15-20 bands
- 99% variance retained
- 10x smaller data = 10x faster training

---

### Challenge 3: Limited Training Data

**Problem:**
- Indian Pines: ~10,000 labeled pixels
- Very small for deep learning
- Risk of overfitting

**Solution:**
- Data augmentation:
  - Random flips (horizontal, vertical)
  - Random rotations (90°, 180°, 270°)
  - Random crops
- Early stopping
- Dropout regularization (0.5)

---

### Challenge 4: Class Imbalance

**Problem:**
- Some classes have 1000+ pixels
- Some have only 100 pixels
- Model biased toward majority classes

**Solution:**
- Weighted loss function
- Oversampling minority classes
- Stratified train/test split

---

### Challenge 5: Computational Resources

**Problem:**
- Deep learning needs GPU
- College laptop only has CPU
- Training takes hours/days

**Solution:**
- Used Google Colab (free GPU access)
- Mixed precision training
- Batch processing
- Saved checkpoints every epoch

---

## 🎯 WHAT TO SAY IN INTERVIEW

### "What is your research project about?"

```
My research project is on hyperspectral image classification for 
remote sensing applications.

Hyperspectral images capture hundreds of wavelength bands for each 
pixel, allowing us to identify materials based on their spectral 
signature.

I implemented a Dual-Scale Feature Extraction network based on 
IEEE TGRS research. The key innovation is using parallel 3×3 and 
5×5 convolutional branches to capture both fine details and global 
context simultaneously.

The model achieves 94.2% accuracy on Indian Pines dataset (16 classes), 
improving over baseline CNN by 5%.
```

---

### "Why did you choose this architecture?"

```
I chose the SSFTT architecture because:

1. Spectral-Spatial: Unlike standard CNNs, it processes both the 
   spectral information (wavelength bands) and spatial information 
   (pixel neighbors) together using 3D convolutions.

2. Transformer: Self-attention helps capture long-range dependencies 
   between pixels, which is important for land-cover classification.

3. Dual-Scale: The parallel 3×3 and 5×5 branches give us the best 
   of both worlds - fine details AND global context.

I modified the original paper by adding the dual-scale module, which 
contributed to the 5% accuracy improvement.
```

---

### "What did you learn from this project?"

```
This project taught me several things:

1. Research Implementation: How to read and implement papers
2. Deep Learning: Architecture design, hyperparameter tuning
3. Optimization: Working with limited computational resources
4. Patience: Results take time, experimentation is key

The biggest lesson was that research papers are starting points, 
not gospel truth. I made modifications based on my understanding 
and achieved better results.
```

---

### "How do you evaluate your model's performance?"

```
I use multiple metrics:

1. Overall Accuracy: Percentage of correctly classified pixels
2. Per-class Accuracy: How each class performs (important for imbalanced data)
3. Confusion Matrix: Shows which classes are confused with each other
4. Classification Maps: Visual output showing classification results

I also use:
- 70/30 train-test split (stratified)
- 5-fold cross-validation for robust evaluation
- Baseline comparison (standard CNN, SVM)
```

---

## 💻 SAMPLE CODE QUESTIONS

### Q: How does PCA work?

```python
# PCA reduces dimensions while preserving variance
from sklearn.decomposition import PCA

pca = PCA(n_components=15)
X_reduced = pca.fit_transform(X)  # 200 bands → 15 components
# 99% of variance retained!
```

---

### Q: How does 3D CNN differ from 2D CNN?

```python
# 2D CNN: H × W → spatial only
# 3D CNN: H × W × Bands → spectral + spatial

# 3D convolution
conv3d = nn.Conv3d(in_channels=15, out_channels=32, kernel_size=(3,3,3))
# Takes 3×3 spatial AND 3 spectral bands at once
```

---

### Q: What is self-attention?

```python
# Self-attention lets each pixel "see" all other pixels
# Key insight: Not all pixels are equally important to each other

attention = softmax(Q @ K.T / sqrt(d_k)) @ V
# Q, K, V are learned queries, keys, values from input features
```