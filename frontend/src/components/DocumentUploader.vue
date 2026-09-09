<template>
  <div class="uploader-container">
    <h2>Subir Nuevo Documento</h2>
    <div
      class="drop-zone"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      :class="{ 'dragging': isDragging }"
    >
      <p v-if="files.length === 0">Arrastra archivos PDF aquí o haz clic para seleccionar</p>
      <div v-else>
        <p>Archivos seleccionados ({{ files.length }}):</p>
        <ul style="list-style: none; padding: 0;">
          <li v-for="f in files" :key="f.name">{{ f.name }}</li>
        </ul>
      </div>
      <input type="file" accept="application/pdf" multiple @change="handleFileSelect" ref="fileInput" class="file-input" />
      <button @click="$refs.fileInput.click()" class="btn-select">Seleccionar PDFs</button>
    </div>

    <div v-if="uploading" class="status processing">
      Procesando documentos ({{ currentUploadIndex }} de {{ files.length }})... por favor espera.
    </div>
    <div v-if="error" class="status error">
      {{ error }}
    </div>
    <div v-if="success" class="status success">
      ¡Documentos procesados exitosamente!
    </div>

    <button @click="uploadFiles" :disabled="files.length === 0 || uploading" class="btn-upload">
      Subir y Procesar
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../services/api';

const files = ref([]);
const isDragging = ref(false);
const uploading = ref(false);
const currentUploadIndex = ref(0);
const error = ref('');
const success = ref(false);

const emit = defineEmits(['document-uploaded']);

// Maneja la selección de archivo vía input
const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files);
  validateAndSetFiles(selectedFiles);
};

// Maneja la selección de archivo vía drag & drop
const handleDrop = (event) => {
  isDragging.value = false;
  const droppedFiles = Array.from(event.dataTransfer.files);
  validateAndSetFiles(droppedFiles);
};

// Valida que sean PDFs y los asigna
const validateAndSetFiles = (selectedFiles) => {
  error.value = '';
  success.value = false;
  const validFiles = selectedFiles.filter(f => f.type === 'application/pdf');

  if (validFiles.length > 0) {
    files.value = [...files.value, ...validFiles];
  } else {
    error.value = 'Por favor, selecciona archivos PDF válidos.';
  }
};

// Llama a la API para subir y procesar los documentos
const uploadFiles = async () => {
  if (files.value.length === 0) return;

  uploading.value = true;
  error.value = '';
  success.value = false;
  currentUploadIndex.value = 0;

  try {
    for (let i = 0; i < files.value.length; i++) {
      currentUploadIndex.value = i + 1;
      await api.extractPdf(files.value[i]);
    }
    success.value = true;
    files.value = []; // Limpiar selección tras éxito
    emit('document-uploaded'); // Notificar al componente padre para refrescar la lista
  } catch (err) {
    console.error("Error al procesar:", err);
    error.value = err.response?.data?.detail || 'No se pudieron procesar todos los PDFs. Verifica que el backend esté en ejecución.';
  } finally {
    uploading.value = false;
  }
};
</script>

<style scoped>
.uploader-container {
  border: 1px solid #ccc;
  padding: 20px;
  border-radius: 8px;
  background-color: #f9f9f9;
  margin-bottom: 20px;
}

.drop-zone {
  border: 2px dashed #999;
  padding: 30px;
  text-align: center;
  border-radius: 8px;
  background-color: #fff;
  transition: all 0.3s ease;
  margin-bottom: 15px;
}

.drop-zone.dragging {
  border-color: #4CAF50;
  background-color: #e8f5e9;
}

.file-input {
  display: none;
}

.btn-select, .btn-upload {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 10px;
}

.btn-upload {
  background-color: #2196F3;
  width: 100%;
}

.btn-upload:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.status {
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  text-align: center;
}

.processing { background-color: #fff3cd; color: #856404; }
.error { background-color: #f8d7da; color: #721c24; }
.success { background-color: #d4edda; color: #155724; }
</style>
