# Gunakan image Node.js sebagai basis
FROM node:14

# Set direktori kerja di dalam container
WORKDIR /app

# Copy file package.json dan package-lock.json
COPY package*.json ./

# Install dependensi aplikasi
RUN npm install

# Copy semua file dari direktori lokal ke dalam container
COPY . .

# Jalankan aplikasi pada port 8080
EXPOSE 8080

# Perintah untuk menjalankan aplikasi
CMD ["npm", "start"]
