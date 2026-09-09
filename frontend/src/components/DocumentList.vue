<template>
  <div class="list-container">
    <h2>Documentos Procesados</h2>

    <div v-if="loading" class="status">Cargando catálogo...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>
    <div v-else-if="documents.length === 0" class="status">
      No hay documentos procesados aún.
    </div>

    <ul v-else class="doc-list">
      <li
        v-for="doc in documents"
        :key="doc.id"
        class="doc-item"
        @click="selectDocument(doc.id)"
      >
        <h3>{{ doc.title }}</h3>
        <p class="meta">
          <span>Páginas: {{ doc.num_pages }}</span>
          <span>Tablas: {{ doc.num_tables }}</span>
          <span>Palabras: {{ doc.total_words }}</span>
        </p>
        <div class="headings-preview" v-if="doc.heading_tree && doc.heading_tree.length">
          <h4>Principales Secciones:</h4>
          <ul>
            <li v-for="(h, idx) in mainHeadings(doc.heading_tree)" :key="idx">
              {{ h.text }}
            </li>
          </ul>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const documents = ref([]);
const loading = ref(true);
const error = ref('');

const emit = defineEmits(['document-selected']);

// Llama al backend para obtener la lista de documentos
const fetchDocuments = async () => {
  loading.value = true;
  error.value = '';
  try {
    const response = await api.listPdfs();
    documents.value = response.data.documents || [];
  } catch (err) {
    console.error("Error obteniendo documentos:", err);
    error.value = 'No se pudo cargar la lista de documentos. ¿Está el backend en ejecución?';
  } finally {
    loading.value = false;
  }
};

// Filtra solo los encabezados principales (H1 y H2) para la vista previa
const mainHeadings = (tree) => {
  return tree.filter(h => h.level <= 2).slice(0, 3);
};

// Emite el evento con el id del documento al seleccionarlo
const selectDocument = (id) => {
  emit('document-selected', id);
};

// Exponer fetchDocuments para que el componente padre (App.vue) lo pueda llamar al subir un nuevo archivo
defineExpose({ fetchDocuments });

onMounted(() => {
  fetchDocuments();
});
</script>

<style scoped>
.list-container {
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
  padding: 20px;
  height: 100%;
}

.status {
  padding: 10px;
  text-align: center;
  color: #666;
}

.error {
  color: #721c24;
  background-color: #f8d7da;
  border-radius: 4px;
}

.doc-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.doc-item {
  background-color: #fff;
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 6px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.doc-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  border-color: #2196F3;
}

.doc-item h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}

.meta {
  font-size: 13px;
  color: #666;
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.headings-preview h4 {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #555;
}

.headings-preview ul {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #777;
}
</style>
