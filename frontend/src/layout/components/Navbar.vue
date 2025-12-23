<template>
  <div class="navbar bg-base-100 shadow-sm">
    <!-- 홈 버튼 -->
    <div class="flex-1">
      <a class="btn btn-ghost text-xl">daisyUI</a>
    </div>

    <!-- 우측 버튼 -->
    <div class="flex-none">
      <ul class="menu menu-horizontal px-1">
        <!-- 로그인 -->
        <li><a>로그인</a></li>
        <!-- 회원정보 셀렉터 -->
        <li>
          <details>
            <summary>반갑습니다! ___님!</summary>
            <ul class="bg-base-100 rounded-t-none p-2">
              <li><a>내 프로필</a></li>
            </ul>
          </details>
        </li>
        <li>
          <ThemeController />
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import ThemeController from './ThemeController.vue'
</script>
