# TalentLens Frontend

Frontend untuk aplikasi TalentLens yang dibangun menggunakan Vue.js.

## Panduan Instalasi dan Menjalankan Lokal

Ikuti langkah-langkah berikut untuk menyiapkan dan menjalankan aplikasi di komputer lokal Anda.

### 1. Konfigurasi Environment Variables

Sebelum menjalankan aplikasi, Anda perlu mengatur variabel environment.

1. Salin file `.env example` menjadi `.env`.
   ```sh
   cp ".env example" .env
   ```
2. Buka file `.env` dan isi nilai untuk variabel-variabel berikut:
   - `VITE_API_URL`: URL endpoint untuk backend API.
   - `VITE_SUPABASE_URL`: URL project Supabase Anda.
   - `VITE_SUPABASE_PUBLISHABLE_KEY`: Public key dari Supabase.
   - `VITE_SUPABASE_ANON_KEY`: Anon key dari Supabase.

### 2. Install Package

Install semua dependensi yang diperlukan menggunakan npm:

```sh
npm install
```

### 3. Menjalankan Aplikasi

Jalankan aplikasi dalam mode development dengan perintah:

```sh
npm run dev
```

Aplikasi biasanya akan berjalan di `http://localhost:5173`.

---

## Panduan Deployment dengan Nixpacks

Berikut adalah panduan untuk men-deploy aplikasi ini menggunakan builder **Nixpacks** dan mengaturnya agar dapat diakses melalui domain pada **Port 80**.

### Persiapan Build & Start
Karena ini adalah aplikasi Single Page Application (SPA), kita perlu mem-build nya menjadi file statis dan kemudian menyajikannya (serve).

1. **Build Command**:
   Nixpacks biasanya akan mendeteksi script build di `package.json`. Pastikan perintah build berjalan:
   ```sh
   npm run build
   ```

2. **Start Command (Serving pada Port 80)**:
   Aplikasi yang sudah di-build berada di folder `dist`. Kita perlu web server ringan untuk menyajikannya. Kita bisa menggunakan `serve`.

   Pada konfigurasi Nixpacks (atau di pengaturan platform deploy seperti Railway/Coolify/Dokploy), atur **Start Command** sebagai berikut:
   
   ```sh
   npx serve -s dist -l 80
   ```
   
   Perintah `-l 80` memastikan aplikasi berjalan dan mendengarkan request pada port 80.

### Setting Domain & Port
Saat mengatur deployment container:

1. **Container Port**: Pastikan container dikonfigurasi untuk mengekspos port **80**.
2. **Domain Mapping**: 
   - Arahkan domain Anda ke server deployment.
   - Di pengaturan Proxy/Domain manager platform Anda, pastikan ia meneruskan trafik dari domain (Public Port 80/443) ke **Internal Port 80** dari container aplikasi ini.

### Ringkasan Konfigurasi Deployment
- **Builder**: Nixpacks
- **Build Command**: `npm run build`
- **Install Command**: `npm install`
- **Output Directory**: `dist`
- **Start Command**: `npx serve -s dist -l 80`
- **Port**: 80
