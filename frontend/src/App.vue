<template>
  <div class="app-container">
    <header class="app-header">
      <h1>Catalogador de Conocimiento PDF</h1>
    </header>

    <main class="app-main">
      <div class="sidebar">
        <DocumentUploader @document-uploaded="refreshList" />
        <DocumentList ref="docListRef" @document-selected="selectDocument" />
      </div>

      <div class="content">
        <MarkdownPreview :document-id="selectedDocumentId" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DocumentUploader from './components/DocumentUploader.vue';
import DocumentList from './components/DocumentList.vue';
import MarkdownPreview from './components/MarkdownPreview.vue';

const docListRef = ref(null);
const selectedDocumentId = ref(null);

// Llama al método del componente hijo para recargar la lista
const refreshList = () => {
  if (docListRef.value) {
    docListRef.value.fetchDocuments();
  }
};

// Actualiza el ID del documento seleccionado para mostrarlo
const selectDocument = (id) => {
  selectedDocumentId.value = id;
};
</script>

<style>
/* Estilos globales básicos */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f0f2f5;
  color: #333;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.app-header {
  background-color: #2c3e50;
  color: white;
  padding: 15px 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 24px;
}

.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
  padding: 20px;
  gap: 20px;
}

.sidebar {
  width: 350px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.content {
  flex: 1;
  height: 100%;
}
</style>
