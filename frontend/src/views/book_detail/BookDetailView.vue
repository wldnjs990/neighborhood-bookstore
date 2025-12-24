<template>
  <main>
    <!-- 상단 섹션 -->
    <section>
      <div class="flex justify-between w-full">
        <figure class="max-w-500 flex-1">
          <img :src="book.cover" :alt="`${book.title} 커버 이미지`" />
        </figure>
        <section class="flex-1">
          <div>북마크</div>
          <h1 class="">{{ book.title }}</h1>
          <p>{{ book.description }}</p>
        </section>
      </div>
    </section>
    <!-- 하단 섹션 -->
    <section></section>
  </main>
</template>

<script setup>
import { getBookDetail } from '@/api/book'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const book = ref({})

onMounted(async () => {
  const data = await getBookDetail(route.params.id)
  console.log(data)
  book.value = data
})
</script>
